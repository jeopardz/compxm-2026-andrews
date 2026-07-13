"""SaaS game-session bridge: resolves the logged-in user's current game and maps
the app's file-based state functions onto Supabase.

The local study app keeps its exact file-based behaviour; every function here runs
ONLY when AUTH_ENABLED is true (app.py guards each call). The on-disk snapshot
model is preserved 1:1 in the DB:

  session_state.game_state (round N)         -> game_snapshots[round = N]      (live)
  session_state.round_snapshots[k] (0..N-1)  -> game_snapshots[round = k]      (rewind points)
  session_state.pending_decisions            -> the live row's pending_json
  bsc_history / board_results                -> games.bsc_history / board_results

so Save, Rewind and Reset behave identically — they just persist to Postgres,
scoped to the user by RLS, and survive across devices and sessions.
"""
from __future__ import annotations

from typing import Optional

import streamlit as st

from sim import db
from sim.auth import current_user_email, current_user_id
from sim.billing import (
    can_create_game, can_reset, render_entitlement_badge, render_paywall,
)
from sim.data.r0_seed import build_r0_state
from sim.data.scenario_pool import load_pool, pick_unplayed
from sim.data.scenarios import build_scenario
from sim.data_models import BoardQueryQuestion, GameState, RoundDecision
from sim.state_migration import normalize_state_dump, rewrite_aliases


# ------------------------------------------------------------------
# current game id
# ------------------------------------------------------------------

def current_game_id() -> Optional[str]:
    return st.session_state.get("current_game_id")


def clear_current_game() -> None:
    st.session_state.pop("current_game_id", None)


# ------------------------------------------------------------------
# load / persist
# ------------------------------------------------------------------

def _hydrate_from_rows(game: dict, rows: list[dict]) -> None:
    """Populate st.session_state from a game header + its snapshot rows."""
    normalized_rows = []
    aliases: dict[str, str] = {}
    for source_row in rows:
        row = dict(source_row)
        state_json = row.get("state_json")
        if isinstance(state_json, dict):
            row["state_json"], found = normalize_state_dump(state_json)
            aliases.update(found)
            if row.get("pending_json") is not None:
                row["pending_json"] = rewrite_aliases(row["pending_json"], found)
        normalized_rows.append(row)
    rows = normalized_rows
    game = dict(game)
    game["bsc_history"] = rewrite_aliases(game.get("bsc_history", []), aliases)
    game["board_results"] = rewrite_aliases(game.get("board_results", {}), aliases)

    n = game["current_round"]
    by_round = {r["round"]: r for r in rows}
    live = by_round.get(n)
    if live is None:
        # Defensive: no row at current_round -> rebuild from scenario at R0.
        st.session_state.game_state = build_scenario(game.get("scenario", "exam-a"))
        st.session_state.pending_decisions = None
    else:
        st.session_state.game_state = GameState.model_validate(live["state_json"])
        pend = live.get("pending_json")
        try:
            st.session_state.pending_decisions = RoundDecision.model_validate(pend) if pend else None
        except Exception:
            st.session_state.pending_decisions = None
    # Rewind points = every snapshot strictly before the live round.
    snaps = {}
    for r in rows:
        if r["round"] < n:
            snaps[str(r["round"])] = {"state": r["state_json"], "pending": r.get("pending_json")}
    st.session_state.round_snapshots = snaps
    st.session_state.bsc_history = game.get("bsc_history", []) or []
    allowed_query_rounds = set(range(1, min(n, 4) + 1))
    if n >= 4:
        allowed_query_rounds.add(5)
    st.session_state.board_results = {
        int(k): v for k, v in (game.get("board_results", {}) or {}).items()
        if int(k) in allowed_query_rounds
    }
    st.session_state.gen_queries = {
        int(k): [BoardQueryQuestion.model_validate(q) for q in questions]
        for k, questions in (game.get("board_queries", {}) or {}).items()
        if int(k) in allowed_query_rounds
    }
    st.session_state.prev_state_snapshot = None


def load_game_into_session(game_id: str) -> bool:
    game = db.load_game_header(game_id)
    if not game:
        return False
    rows = db.list_snapshots(game_id)
    _hydrate_from_rows(game, rows)
    st.session_state.current_game_id = game_id
    st.session_state["_game_updated_at"] = game.get("updated_at")
    return True


def persist_session_to_db() -> None:
    """Write the whole current session (live state + rewind points + header) to the
    DB. Called wherever the local app calls save_state()."""
    game_id = current_game_id()
    if not game_id:
        return
    state: GameState = st.session_state.game_state
    pending: Optional[RoundDecision] = st.session_state.get("pending_decisions")
    n = state.round_num

    # Claim the game revision before mutating snapshots. A stale browser tab fails
    # here without overwriting the newer tab's state.
    status = "completed" if n >= 4 else "active"
    new_revision = db.update_game_header(
        game_id, current_round=n, status=status,
        bsc_history=st.session_state.get("bsc_history", []),
        board_results={str(k): v for k, v in st.session_state.get("board_results", {}).items()},
        board_queries={str(k): [q.model_dump() for q in values]
                       for k, values in st.session_state.get("gen_queries", {}).items()},
        expected_updated_at=st.session_state.get("_game_updated_at"),
    )

    # Live row (current round).
    db.save_snapshot(game_id, n,
                     state.model_dump(),
                     pending.model_dump() if pending else None)
    # Rewind points (0..N-1). Small (<=4 rows) so upserting all is cheap and keeps
    # the DB authoritative even after a rewind rewrote the timeline.
    for k, snap in st.session_state.get("round_snapshots", {}).items():
        if int(k) != n:
            db.save_snapshot(game_id, int(k), snap["state"], snap.get("pending"))

    st.session_state["_game_updated_at"] = new_revision


def persist_snapshot(round_num: int, state_dump: dict, pending_dump: Optional[dict]) -> None:
    """Snapshots are flushed by persist_session_to_db after its revision claim."""


def rewind_db(target_round: int) -> None:
    """Delete the rewritten future timeline in the DB (session already restored)."""
    game_id = current_game_id()
    if game_id:
        new_revision = db.update_game_header(
            game_id, current_round=target_round, status="active",
            bsc_history=st.session_state.get("bsc_history", []),
            board_results={str(k): v for k, v in st.session_state.get("board_results", {}).items()},
            board_queries={str(k): [q.model_dump() for q in values]
                           for k, values in st.session_state.get("gen_queries", {}).items()},
            expected_updated_at=st.session_state.get("_game_updated_at"),
        )
        db.delete_snapshots_after(game_id, target_round)
        st.session_state["_game_updated_at"] = new_revision


# ------------------------------------------------------------------
# create / reset
# ------------------------------------------------------------------

def create_game(scenario_id: str, label: str) -> Optional[str]:
    uid = current_user_id()
    if not uid:
        return None
    state = build_scenario(scenario_id)
    try:
        game_id = db.create_game(uid, state.model_dump(), label=label, scenario=scenario_id)
    except Exception:
        st.warning("The demo game has already been used. Upgrade to start another game.")
        return None
    if game_id:
        load_game_into_session(game_id)
    return game_id


def reset_game_to_start() -> None:
    """Reset the CURRENT game back to its scenario's round 0 (keeps the same game
    row and scenario, wipes progress)."""
    game_id = current_game_id()
    if not game_id:
        return
    game = db.load_game_header(game_id)
    scenario_id = game.get("scenario", "exam-a") if game else "exam-a"
    state = build_scenario(scenario_id)
    db.update_game_header(game_id, current_round=0, status="active",
                          bsc_history=[], board_results={}, board_queries={},
                          expected_updated_at=st.session_state.get("_game_updated_at"))
    db.delete_snapshots_after(game_id, -1)  # remove ALL snapshots after revision claim
    db.save_snapshot(game_id, 0, state.model_dump(), None)
    load_game_into_session(game_id)


# ------------------------------------------------------------------
# My Games hub (Phase 2)
# ------------------------------------------------------------------

def _scenario_label(scenario_id: str) -> str:
    from sim.data.scenario_pool import get_entry
    entry = get_entry(scenario_id)
    if entry:
        return f"{entry['difficulty']}"
    return "Reference" if scenario_id in ("exam-a", "base") else scenario_id


def render_game_hub() -> None:
    """The My Games screen: list, resume, new, rename, delete. Renders and stops
    the script until a game is active. Call only in SaaS mode."""
    st.title("My Games")
    render_entitlement_badge(sidebar=False)
    st.caption(f"Signed in as {current_user_email()}")

    uid = current_user_id()
    games = db.list_games(uid)

    # ---- New game ----
    with st.expander("➕ New game", expanded=not games):
        if not can_create_game(len(games)):
            st.warning("The free demo includes one game. Upgrade to start more.")
            render_paywall("new_game")
        else:
            pool = load_pool()
            diffs = ["Any", "Easy", "Normal", "Hard"] if pool else ["Reference"]
            col1, col2 = st.columns([1, 1])
            with col1:
                choice = st.selectbox("Difficulty", diffs, key="new_game_difficulty")
            with col2:
                label = st.text_input("Name", value="My Game", key="new_game_label")
            if st.button("Start new game", type="primary", width="stretch"):
                if not pool:
                    scenario_id = "exam-a"
                else:
                    played = [g["scenario"] for g in games]
                    diff = None if choice == "Any" else choice
                    entry = pick_unplayed(played, difficulty=diff)
                    scenario_id = entry["id"] if entry else "exam-a"
                if create_game(scenario_id, label.strip() or "My Game"):
                    st.rerun()

    # ---- Existing games ----
    if not games:
        st.info("No games yet — start one above.")
        st.stop()

    st.subheader("Your games")
    for g in games:
        gid = g["id"]
        c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
        with c1:
            st.markdown(f"**{g['label']}**  \n"
                        f"<span style='color:#718096;font-size:12px'>"
                        f"{_scenario_label(g['scenario'])} · Round {g['current_round']}/4 · "
                        f"{g['status']}</span>", unsafe_allow_html=True)
        with c2:
            if st.button("▶ Resume", key=f"resume_{gid}", width="stretch"):
                if load_game_into_session(gid):
                    st.rerun()
        with c3:
            if st.button("Reset", key=f"reset_{gid}", width="stretch",
                         disabled=not can_reset()):
                st.session_state["_confirm_reset"] = gid
        with c4:
            if st.button("Delete", key=f"del_{gid}", width="stretch"):
                st.session_state["_confirm_delete"] = gid

        if st.session_state.get("_confirm_reset") == gid:
            st.warning(f"Reset '{g['label']}' back to Round 0? Progress is lost.")
            if st.button("Yes, reset", key=f"cr_{gid}", type="primary"):
                load_game_into_session(gid)
                reset_game_to_start()
                st.session_state.pop("_confirm_reset", None)
                st.rerun()
        if st.session_state.get("_confirm_delete") == gid:
            st.error(f"Delete '{g['label']}' permanently?")
            if st.button("Yes, delete", key=f"cd_{gid}", type="primary"):
                db.delete_game(gid)
                if current_game_id() == gid:
                    clear_current_game()
                st.session_state.pop("_confirm_delete", None)
                st.rerun()

    st.stop()  # never fall through to the game UI without a resumed game


def render_hub_controls_in_sidebar() -> None:
    """Back-to-hub button + rename, shown in the sidebar while a game is active."""
    if not current_game_id():
        return
    with st.sidebar:
        if st.button("← My Games", width="stretch"):
            clear_current_game()
            st.rerun()
