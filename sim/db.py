"""Persistence layer for the SaaS build (Supabase Postgres).

Every function uses the caller's authenticated Supabase client (from
sim.auth.get_supabase after login), so Row Level Security scopes all reads and
writes to the current user automatically — there is no way to touch another
user's data even if a query is written carelessly.

The game state is stored exactly as the local save file already serializes it:
GameState.model_dump() -> games/game_snapshots.state_json (jsonb), and
RoundDecision.model_dump() -> game_snapshots.pending_json. So round-tripping is
the same Pydantic (de)serialization the app already relies on — see
test_db_roundtrip.py.

`supabase` is imported lazily by sim.auth.get_supabase.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _client():
    from sim.auth import get_supabase
    return get_supabase()


# ------------------------------------------------------------------
# games
# ------------------------------------------------------------------

def list_games(user_id: str) -> list[dict]:
    res = (_client().table("games")
           .select("*")
           .eq("user_id", user_id)
           .order("updated_at", desc=True)
           .execute())
    return res.data or []


def create_game(user_id: str, state_json: dict, label: str = "My Game",
                scenario: str = "exam-a") -> Optional[str]:
    """Atomically consume the demo allowance and create a game + R0 snapshot."""
    res = _client().rpc("create_game", {
        "p_label": label, "p_scenario": scenario, "p_state_json": state_json,
    }).execute()
    data = res.data
    if isinstance(data, list):
        data = data[0] if data else None
    if isinstance(data, dict):
        return data.get("game_id") or data.get("id")
    return str(data) if data else None


def load_game_header(game_id: str) -> Optional[dict]:
    """Return just the game row (label, scenario, current_round, status, history)."""
    res = _client().table("games").select("*").eq("id", game_id).maybe_single().execute()
    return res.data if res and res.data else None


def rename_game(game_id: str, label: str) -> None:
    _client().table("games").update({"label": label}).eq("id", game_id).execute()


def delete_game(game_id: str) -> None:
    # game_snapshots cascade-delete via FK on games.
    _client().table("games").delete().eq("id", game_id).execute()


def update_game_header(game_id: str, current_round: int, status: str,
                       bsc_history: list, board_results: dict,
                       board_queries: Optional[dict] = None,
                       expected_updated_at: Optional[str] = None) -> str:
    """Optimistically update the header and return its new revision."""
    res = _client().rpc("update_game_header", {
        "p_game_id": game_id, "p_expected_updated_at": expected_updated_at,
        "p_current_round": current_round, "p_status": status,
        "p_bsc_history": bsc_history, "p_board_results": board_results,
        "p_board_queries": board_queries or {},
    }).execute()
    data = res.data
    if isinstance(data, list):
        data = data[0] if data else None
    if not data:
        raise RuntimeError("This game changed in another tab. Reload before saving.")
    if isinstance(data, dict):
        return str(data.get("updated_at") or data.get("new_updated_at"))
    return str(data)


def game_updated_at(game_id: str) -> Optional[str]:
    """Cheap freshness probe for the two-tabs-open guard."""
    res = _client().table("games").select("updated_at").eq("id", game_id).single().execute()
    return res.data.get("updated_at") if res.data else None


# ------------------------------------------------------------------
# snapshots (Rewind / autosave)
# ------------------------------------------------------------------

def save_snapshot(game_id: str, rnd: int, state_json: dict,
                  pending_json: Optional[dict]) -> None:
    """Upsert the snapshot for a round (Rewind restores these)."""
    _client().table("game_snapshots").upsert({
        "game_id": game_id, "round": rnd, "state_json": state_json,
        "pending_json": pending_json, "schema_version": 1, "saved_at": _utcnow(),
    }).execute()


def load_snapshot(game_id: str, rnd: int) -> Optional[dict]:
    res = (_client().table("game_snapshots")
           .select("*").eq("game_id", game_id).eq("round", rnd)
           .maybe_single().execute())
    return res.data if res and res.data else None


def list_snapshots(game_id: str) -> list[dict]:
    """All snapshot rows for a game (round, state_json, pending_json), ascending."""
    res = (_client().table("game_snapshots")
           .select("round, state_json, pending_json")
           .eq("game_id", game_id).order("round").execute())
    return res.data or []


def delete_snapshots_after(game_id: str, rnd: int) -> None:
    """Drop the rewritten future timeline when the player rewinds to `rnd`."""
    (_client().table("game_snapshots")
     .delete().eq("game_id", game_id).gt("round", rnd).execute())


# ------------------------------------------------------------------
# entitlements
# ------------------------------------------------------------------

def get_active_entitlement(user_id: str) -> Optional[dict]:
    """Most recent entitlement whose expires_at is still in the future, or None."""
    res = (_client().table("entitlements")
           .select("*")
           .eq("user_id", user_id)
           .gt("expires_at", _utcnow())
           .order("expires_at", desc=True)
           .limit(1)
           .execute())
    data = res.data or []
    return data[0] if data else None
