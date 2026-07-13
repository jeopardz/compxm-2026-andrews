"""Entitlement gating + paywall for the SaaS build.

Business rules (confirmed with the user):
  * Demo (no active entitlement): may create ONE game and advance R0 -> R1 only.
    No rewind, no reset, no further rounds.
  * Full access (active entitlement, $12.99 / 30-day): unlimited games, all four
    rounds, rewind and reset.
  * If an entitlement expires mid-game the player keeps read-only access to all
    existing data — advancing is blocked, but nothing is locked away or deleted.

LOCAL MODE (AUTH_ENABLED False) bypasses every gate.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

import streamlit as st

from sim.auth import auth_enabled, current_user_email, current_user_id

_CACHE_TTL_SECONDS = 60
DEMO_MAX_GAMES = 1
DEMO_MAX_ROUND = 1  # demo may reach round 1 (i.e. advance R0 -> R1) and no further


# ------------------------------------------------------------------
# access checks
# ------------------------------------------------------------------

def _active_entitlement(user_id: str) -> Optional[dict]:
    from sim.db import get_active_entitlement
    return get_active_entitlement(user_id)


def has_full_access(user_id: Optional[str] = None) -> bool:
    """True if the user has an unexpired entitlement. Cached ~60s in session_state
    so we don't hit the DB on every Streamlit rerun. Call invalidate_access_cache()
    after a purchase check."""
    if not auth_enabled():
        return True  # local study mode: never gated
    user_id = user_id or current_user_id()
    if not user_id:
        return False
    cache = st.session_state.get("_full_access_cache")
    now = time.time()
    if cache and cache.get("user_id") == user_id and now - cache["at"] < _CACHE_TTL_SECONDS:
        return cache["value"]
    value = _active_entitlement(user_id) is not None
    st.session_state["_full_access_cache"] = {"user_id": user_id, "value": value, "at": now}
    return value


def invalidate_access_cache() -> None:
    st.session_state.pop("_full_access_cache", None)


def entitlement_days_left(user_id: Optional[str] = None) -> Optional[int]:
    if not auth_enabled():
        return None
    ent = _active_entitlement(user_id or current_user_id() or "")
    if not ent:
        return None
    try:
        expires = datetime.fromisoformat(ent["expires_at"].replace("Z", "+00:00"))
        delta = expires - datetime.now(timezone.utc)
        return max(0, delta.days)
    except Exception:
        return None


def can_advance(current_round: int, user_id: Optional[str] = None) -> tuple[bool, str]:
    """May the player advance from `current_round` to the next one?"""
    if not auth_enabled():
        return True, ""
    if current_round < DEMO_MAX_ROUND:
        return True, ""                       # demo: R0 -> R1 always free
    if has_full_access(user_id):
        return True, ""
    return False, "paywall"


def can_create_game(existing_game_count: int, user_id: Optional[str] = None) -> bool:
    if not auth_enabled():
        return True
    if has_full_access(user_id):
        return True
    return existing_game_count < DEMO_MAX_GAMES


def can_rewind(user_id: Optional[str] = None) -> bool:
    return not auth_enabled() or has_full_access(user_id)


def can_reset(user_id: Optional[str] = None) -> bool:
    return not auth_enabled() or has_full_access(user_id)


# ------------------------------------------------------------------
# paywall UI
# ------------------------------------------------------------------

def checkout_url(user_id: Optional[str] = None, email: Optional[str] = None) -> str:
    """Lemon Squeezy checkout link with the user id passed as custom data so the
    webhook can attach the purchase to the right account."""
    from sim.auth import _secret
    base = _secret("LEMONSQUEEZY_CHECKOUT_URL", "") or ""
    uid = user_id or current_user_id() or ""
    mail = email or current_user_email() or ""
    if not base:
        return ""
    sep = "&" if "?" in base else "?"
    query = urlencode({"checkout[custom][user_id]": uid, "checkout[email]": mail})
    return f"{base}{sep}{query}"


def render_paywall(context: str = "advance") -> None:
    """Show the upgrade card. `context` tailors the headline (advance/new game/etc)."""
    heads = {
        "advance": "Unlock rounds 2–4",
        "new_game": "Unlock unlimited games",
        "rewind": "Unlock Rewind",
        "reset": "Unlock Reset",
    }
    st.subheader(heads.get(context, "Upgrade to full access"))
    st.write(
        "You've finished the free demo round. Upgrade to play all four rounds, "
        "replay and reset as many puzzles as you like, and use Rewind."
    )

    col_demo, col_full = st.columns(2)
    with col_demo:
        st.markdown("**Demo — free**")
        st.markdown("- 1 game\n- Round 1 only\n- No rewind / reset")
    with col_full:
        st.markdown("**Full — $12.99 / 30 days**")
        st.markdown("- Unlimited games\n- All 4 rounds\n- Rewind + reset\n- Every difficulty")

    url = checkout_url()
    if url:
        st.link_button("Upgrade — $12.99", url, width="stretch", type="primary")
    else:
        st.info("Checkout is not configured yet (set LEMONSQUEEZY_CHECKOUT_URL).")

    if st.button("I've paid — refresh my access", width="stretch"):
        invalidate_access_cache()
        st.rerun()


def render_entitlement_badge(sidebar: bool = True) -> None:
    """Small status line: shows days left, or a demo notice."""
    if not auth_enabled():
        return
    target = st.sidebar if sidebar else st
    days = entitlement_days_left()
    if days is not None:
        target.success(f"Full access — {days} day(s) left")
    else:
        target.info("Demo mode — round 1 only")
