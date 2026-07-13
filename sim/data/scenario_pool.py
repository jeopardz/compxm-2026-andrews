"""Loader + selector for the pre-validated scenario pool.

The pool (sim/data/scenario_pool.json) is produced offline by
scripts/build_scenario_pool.py — every entry has already passed the full
validation gauntlet, so anything selected here is guaranteed playable to the end
of round 4. In the SaaS build the same data lives in the Supabase `scenarios`
table and selection filters by what the user has already played; this module is
the local/offline equivalent and the shared selection logic.
"""
from __future__ import annotations

import json
import random
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional

from sim.data.scenarios import build_scenario
from sim.data_models import GameState

POOL_PATH = Path(__file__).resolve().parent / "scenario_pool.json"


@lru_cache(maxsize=1)
def load_pool() -> list[dict]:
    """Return the list of validated scenario entries (empty if the pool is absent)."""
    if not POOL_PATH.exists():
        return []
    data = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    return data.get("scenarios", [])


def get_entry(scenario_id: str) -> Optional[dict]:
    for entry in load_pool():
        if entry["id"] == scenario_id:
            return entry
    return None


def pick_unplayed(played_ids: Iterable[str] = (), difficulty: Optional[str] = None,
                  rng: Optional[random.Random] = None) -> Optional[dict]:
    """Pick a validated scenario the user hasn't played yet.

    Filters by measured difficulty when given. Falls back to replaying the least
    recently used pool once every scenario has been played. Returns None only if
    the pool is empty. Once chosen, the entry's id fully reproduces the board.
    """
    played = set(played_ids)
    pool = load_pool()
    if not pool:
        return None
    candidates = [e for e in pool if difficulty is None or e["difficulty"] == difficulty]
    if not candidates:
        candidates = pool
    fresh = [e for e in candidates if e["id"] not in played]
    chooser = rng or random
    return chooser.choice(fresh or candidates)


def build_from_entry(entry: dict) -> GameState:
    return build_scenario(entry["id"])
