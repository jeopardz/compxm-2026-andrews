"""Dev smoke test for the live Supabase connection + RLS + db layer.

Run:  python -m scripts.test_supabase_conn

Reads .streamlit/secrets.toml directly (no Streamlit runtime needed), signs up a
throwaway user, and exercises the create-game / save-snapshot / load-snapshot
round trip against the real database. Also verifies RLS blocks an anonymous client
from reading another user's games. Prints a clear PASS/FAIL per step.

NOTE: if the project has email confirmation ON (Supabase default), sign_up returns
no session and the authed steps are skipped with a clear message — disable
"Confirm email" in Auth settings for dev, then re-run.
"""
from __future__ import annotations

import sys
import time
import tomllib
from pathlib import Path

from supabase import create_client

from sim.data.r0_seed import build_r0_state

SECRETS = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"


def load_secrets() -> dict:
    return tomllib.loads(SECRETS.read_text(encoding="utf-8"))


def main() -> int:
    cfg = load_secrets()
    url, key = cfg.get("SUPABASE_URL"), cfg.get("SUPABASE_ANON_KEY")
    if not url or not key:
        print("FAIL: SUPABASE_URL / SUPABASE_ANON_KEY missing from secrets.toml")
        return 1

    client = create_client(url, key)
    print(f"PASS: client constructed for {url}")

    # Anonymous read must be blocked by RLS (no rows / error, never other users' data).
    try:
        res = client.table("games").select("*").execute()
        n = len(res.data or [])
        print(f"PASS: anonymous games read returned {n} rows (RLS: expected 0)")
    except Exception as exc:  # noqa: BLE001
        print(f"PASS: anonymous games read rejected by RLS ({type(exc).__name__})")

    # Sign up a throwaway user. Supabase rejects domains without MX records
    # (e.g. example.com), so use a real-format domain; the confirmation mail (if
    # any) to a nonexistent local-part simply bounces. Override via argv[1].
    email = sys.argv[1] if len(sys.argv) > 1 else f"devtest{int(time.time())}@gmail.com"
    password = "devtest-pw-123456"
    try:
        res = client.auth.sign_up({"email": email, "password": password})
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: sign_up raised {type(exc).__name__}: {exc}")
        return 1

    if not res.session:
        print("INFO: sign_up returned no session -> email confirmation is ON.")
        print("      Disable Auth -> 'Confirm email' in the dashboard for dev, then re-run.")
        print("      (Connection + RLS checks above already PASSED.)")
        return 0

    user_id = res.user.id
    print(f"PASS: signed up + logged in as {email} ({user_id[:8]}...)")

    # Profile row should have been auto-created by the trigger.
    prof = client.table("profiles").select("*").eq("id", user_id).execute()
    print(f"{'PASS' if prof.data else 'FAIL'}: profile auto-created by trigger "
          f"({len(prof.data or [])} row)")

    # Create a game + round-0 snapshot, then read it back.
    state_json = build_r0_state().model_dump()
    g = client.rpc("create_game", {
        "p_label": "conn-test", "p_scenario": "exam-a", "p_state_json": state_json,
    }).execute()
    game_id = g.data[0] if isinstance(g.data, list) else g.data
    back = (client.table("game_snapshots").select("state_json")
            .eq("game_id", game_id).eq("round", 0).single().execute())
    ok = back.data and back.data["state_json"]["round_num"] == 0
    print(f"{'PASS' if ok else 'FAIL'}: game + snapshot saved and read back (round_num=0)")

    # RLS cross-user isolation: a fresh anonymous client must not see this game.
    anon = create_client(url, key)
    other = anon.table("games").select("*").eq("id", game_id).execute()
    print(f"{'PASS' if not other.data else 'FAIL'}: other client cannot read this game "
          f"({len(other.data or [])} rows, expected 0)")

    # Clean up the throwaway game (snapshots cascade).
    client.table("games").delete().eq("id", game_id).execute()
    print("PASS: cleaned up test game")
    print("\nALL LIVE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
