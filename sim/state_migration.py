"""Normalize pre-rebrand game snapshots to the current CompMastery names.

The simulator has a fixed four-company/four-product board.  Older local saves
and development database snapshots can therefore be upgraded safely by company
initial and product order, without keeping legacy brand names in the product
source.  The functions are intentionally pure: callers decide whether to write
the normalized payload back to disk or the database.
"""
from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Mapping


COMPANY_BY_INITIAL = {
    "A": "Apex",
    "B": "Borealis",
    "C": "Crestline",
    "D": "Dynamo",
}

PRODUCTS_BY_COMPANY = {
    "Apex": ("Atlas", "Axiom", "Arc", "Aura"),
    "Borealis": ("Beacon", "Brio", "Bloom", "Bolt"),
    "Crestline": ("Cedar", "Coda", "Crest", "Cove"),
    "Dynamo": ("Delta", "Dune", "Drift", "Dusk"),
}


def _current_company_name(value: Any) -> str | None:
    text = str(value or "")
    return COMPANY_BY_INITIAL.get(text[:1].upper())


def _rewrite_text(text: str, aliases: Mapping[str, str]) -> str:
    rewritten = text
    for old, new in sorted(aliases.items(), key=lambda item: len(item[0]), reverse=True):
        if not old or old == new:
            continue
        if rewritten == old:
            rewritten = new
            continue
        old_prefix = f"{old.lower()}_"
        if rewritten.startswith(old_prefix):
            rewritten = f"{new.lower()}_{rewritten[len(old_prefix):]}"
        rewritten = re.sub(rf"\b{re.escape(old)}\b", new, rewritten)
    return rewritten


def rewrite_aliases(value: Any, aliases: Mapping[str, str]) -> Any:
    """Recursively rewrite dictionary keys and string values using aliases."""
    if isinstance(value, dict):
        return {
            _rewrite_text(key, aliases) if isinstance(key, str) else key:
            rewrite_aliases(item, aliases)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [rewrite_aliases(item, aliases) for item in value]
    if isinstance(value, tuple):
        return tuple(rewrite_aliases(item, aliases) for item in value)
    if isinstance(value, str):
        return _rewrite_text(value, aliases)
    return value


def normalize_state_dump(state_dump: Mapping[str, Any]) -> tuple[dict, dict[str, str]]:
    """Return a current-name state dump plus aliases found while normalizing it."""
    state = deepcopy(dict(state_dump))
    aliases: dict[str, str] = {}

    for company in state.get("companies", []):
        old_company = str(company.get("name", ""))
        new_company = _current_company_name(old_company)
        if not new_company:
            continue
        aliases[old_company] = new_company
        company["name"] = new_company

        target_products = PRODUCTS_BY_COMPANY[new_company]
        for index, product in enumerate(company.get("products", [])):
            if index >= len(target_products):
                break
            old_product = str(product.get("name", ""))
            new_product = target_products[index]
            aliases[old_product] = new_product
            product["name"] = new_product
            product["company"] = new_company

    return rewrite_aliases(state, aliases), aliases


def normalize_save_payload(payload: Mapping[str, Any]) -> dict:
    """Normalize a complete local ``save_state.json`` payload."""
    result = deepcopy(dict(payload))
    aliases: dict[str, str] = {}

    game_state = result.get("game_state")
    if isinstance(game_state, Mapping):
        result["game_state"], found = normalize_state_dump(game_state)
        aliases.update(found)

    snapshots = result.get("round_snapshots", {})
    if isinstance(snapshots, dict):
        for snapshot in snapshots.values():
            if not isinstance(snapshot, dict) or not isinstance(snapshot.get("state"), Mapping):
                continue
            snapshot["state"], found = normalize_state_dump(snapshot["state"])
            aliases.update(found)
            if snapshot.get("pending") is not None:
                snapshot["pending"] = rewrite_aliases(snapshot["pending"], found)

    if result.get("pending_decisions") is not None:
        result["pending_decisions"] = rewrite_aliases(result["pending_decisions"], aliases)

    for key in ("bsc_history", "board_results"):
        if key in result:
            result[key] = rewrite_aliases(result[key], aliases)

    return result
