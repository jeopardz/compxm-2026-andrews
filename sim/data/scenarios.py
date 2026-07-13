"""
Scenario generator for the SaaS product.

Produces varied-but-valid starting states ("exam scenarios") by perturbing the
base R0 seed deterministically from an integer seed. Every scenario is:
  - deterministic: the same scenario_id always rebuilds the exact same board,
    so Reset returns the player to an identical puzzle.
  - balance-sheet consistent: after perturbation each company's books are
    re-balanced so total_assets == total_liabilities + total_equity.

A generated scenario is NOT guaranteed playable on its own — it must pass
`sim.data.scenario_validator.validate_scenario` before being served to a user.
The pre-built pool (scripts/build_scenario_pool.py) only keeps validated seeds.

Scenario id conventions:
  - "exam-a" / "base" / ""  -> the untouched R0 seed (reference puzzle)
  - "gen-<int>"             -> generate_scenario(<int>)
  - anything else           -> generate_scenario(stable_hash(id))
"""
from __future__ import annotations

import hashlib
from math import sqrt
from random import Random
from typing import Optional

from sim.data.r0_seed import build_r0_state
from sim.data_models import Company, GameState, Product, Segment


BASE_SCENARIO_IDS = ("exam-a", "base", "")

PLAYER_COMPANY = "Apex"  # the company controlled by the human player

DIFFICULTIES = ("easy", "normal", "hard")

# How each difficulty biases the puzzle. "Harder" means the PLAYER starts weaker
# (older, costlier, less cash) and competitors start stronger (fresher, better
# known), so a competent player scores lower — which the validator then confirms
# by measuring the baseline playthrough's BSC. Levers avoid product position so
# they never push a product out of its rough-cut circle (that would just get the
# scenario rejected instead of graded).
DIFFICULTY_BIAS = {
    "easy":   {"player_age": -1.0, "player_cost": -0.08, "player_cash": 0.20,
               "comp_awareness": -0.10, "comp_age": 0.8},
    "normal": {"player_age": 0.0, "player_cost": 0.0, "player_cash": 0.0,
               "comp_awareness": 0.0, "comp_age": 0.0},
    "hard":   {"player_age": 1.6, "player_cost": 0.08, "player_cash": -0.20,
               "comp_awareness": 0.08, "comp_age": -0.4},
}


# ------------------------------------------------------------------
# id <-> seed
# ------------------------------------------------------------------

def stable_hash(text: str) -> int:
    """Process-independent hash (Python's built-in hash() is salted per run)."""
    digest = hashlib.md5(text.encode("utf-8")).hexdigest()
    return int(digest, 16) % (2 ** 31)


def parse_scenario_id(scenario_id: str) -> tuple[Optional[int], Optional[str]]:
    """Parse a scenario id into (seed, difficulty).

    Forms:
      "exam-a"/"base"/""        -> (None, None)      base puzzle
      "gen-<seed>"              -> (<seed>, None)     difficulty derived from seed
      "gen-<seed>-<difficulty>" -> (<seed>, <diff>)   difficulty pinned
      anything else             -> (stable_hash(id), None)
    """
    if scenario_id in BASE_SCENARIO_IDS:
        return None, None
    if scenario_id.startswith("gen-"):
        parts = scenario_id.split("-")
        try:
            seed = int(parts[1])
        except (IndexError, ValueError):
            return stable_hash(scenario_id), None
        difficulty = parts[2] if len(parts) > 2 and parts[2] in DIFFICULTIES else None
        return seed, difficulty
    return stable_hash(scenario_id), None


def seed_to_scenario_id(seed: int, difficulty: Optional[str] = None) -> str:
    return f"gen-{seed}-{difficulty}" if difficulty else f"gen-{seed}"


# ------------------------------------------------------------------
# perturbation helpers
# ------------------------------------------------------------------

def _jitter(rng: Random, value: float, pct: float) -> float:
    """Multiplicative jitter within +/- pct (e.g. 0.05 = +/-5%)."""
    return value * (1.0 + rng.uniform(-pct, pct))


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _clamp_position_to_rough_cut(pfmn: float, size: float, seg: Segment,
                                 max_dist: float = 3.5) -> tuple[float, float]:
    """Keep a product inside its primary segment's rough-cut circle (radius 4.0),
    leaving a small margin so year-of-drift doesn't immediately push it out."""
    dx = pfmn - seg.center_pfmn
    dy = size - seg.center_size
    dist = sqrt(dx * dx + dy * dy)
    if dist > max_dist and dist > 0:
        scale = max_dist / dist
        pfmn = seg.center_pfmn + dx * scale
        size = seg.center_size + dy * scale
    return round(pfmn, 1), round(size, 1)


def _rebalance_company(company: Company) -> None:
    """Set retained_earnings so the balance sheet identity holds after perturbation:
        total_assets == total_liabilities + total_equity
    (retained_earnings is the plug; common_stock and everything else stay as jittered)."""
    net_plant = company.plant_value - company.accumulated_depreciation
    total_assets = (company.cash + company.accounts_receivable
                    + company.inventory_value + net_plant)
    total_liabilities = (company.accounts_payable + company.current_debt
                         + sum(b.face_value for b in company.bonds))
    company.retained_earnings = round(
        total_assets - total_liabilities - company.common_stock, 0
    )


def _perturb_product(rng: Random, p: Product, seg: Segment) -> None:
    # Position: nudge then clamp inside the rough-cut circle
    p.pfmn = _jitter(rng, p.pfmn, 0.06)
    p.size = _jitter(rng, p.size, 0.06)
    p.pfmn, p.size = _clamp_position_to_rough_cut(p.pfmn, p.size, seg)

    # MTBF: nudge, keep near the segment band, round to nearest 500
    mtbf = _jitter(rng, p.mtbf, 0.06)
    mtbf = _clamp(mtbf, seg.mtbf_min - 2000, seg.mtbf_max + 2000)
    p.mtbf = int(round(mtbf / 500.0) * 500)

    # Age: nudge, keep sane (never brand-new-negative, never ancient)
    p.age = round(_clamp(_jitter(rng, max(p.age, 0.5), 0.20), 0.3, 6.0), 1)

    # Price: nudge, keep within the segment band
    price = _jitter(rng, p.price, 0.05)
    p.price = round(_clamp(price, seg.price_min, seg.price_max), 2)

    # Unit costs: nudge modestly
    p.material_cost = round(max(1.0, _jitter(rng, p.material_cost, 0.06)), 2)
    p.labor_cost = round(max(0.5, _jitter(rng, p.labor_cost, 0.06)), 2)

    # Capacity: nudge, round to nearest 10, floor at 100
    cap = _jitter(rng, p.capacity_first_shift, 0.10)
    p.capacity_first_shift = max(100, int(round(cap / 10.0) * 10))

    # Automation: occasionally +/-1 level, clamp 1..10
    if rng.random() < 0.5:
        p.automation = _clamp(round(p.automation + rng.choice([-1.0, 1.0]), 1), 1.0, 10.0)

    # Inventory + last-round volumes: nudge (drive AI forecast baseline variety)
    p.inventory = max(0, int(_jitter(rng, max(p.inventory, 1), 0.20)))
    p.units_sold_last = max(50, int(_jitter(rng, max(p.units_sold_last, 50), 0.10)))
    p.units_produced_last = max(50, int(_jitter(rng, max(p.units_produced_last, 50), 0.10)))

    # Awareness / accessibility: nudge, clamp 0..1
    p.awareness = round(_clamp(_jitter(rng, max(p.awareness, 0.3), 0.08), 0.30, 0.95), 2)
    for key in list(p.accessibility.keys()):
        p.accessibility[key] = round(
            _clamp(_jitter(rng, max(p.accessibility[key], 0.3), 0.08), 0.30, 0.95), 2
        )

    # Marketing budgets: nudge
    p.promo_budget = round(_jitter(rng, p.promo_budget, 0.10), 0)
    p.sales_budget = round(_jitter(rng, p.sales_budget, 0.10), 0)


def _perturb_company_financials(rng: Random, c: Company) -> None:
    c.cash = round(_jitter(rng, c.cash, 0.10), 0)
    c.current_debt = round(max(0.0, _jitter(rng, c.current_debt, 0.10)), 0)
    c.accounts_receivable = round(max(0.0, _jitter(rng, c.accounts_receivable, 0.08)), 0)
    c.accounts_payable = round(max(0.0, _jitter(rng, c.accounts_payable, 0.08)), 0)
    c.inventory_value = round(max(0.0, _jitter(rng, c.inventory_value, 0.10)), 0)
    # plant + accumulated depreciation move together modestly (keep net plant > 0)
    c.plant_value = round(_jitter(rng, c.plant_value, 0.06), 0)
    c.accumulated_depreciation = round(
        _clamp(_jitter(rng, c.accumulated_depreciation, 0.06), 0.0, c.plant_value * 0.85), 0
    )
    _rebalance_company(c)


# ------------------------------------------------------------------
# public API
# ------------------------------------------------------------------

def _apply_difficulty_bias(state: GameState, difficulty: str) -> None:
    """Nudge player/competitor starting strength toward a target difficulty.
    Applied after the random perturbation; books are re-balanced afterward."""
    bias = DIFFICULTY_BIAS.get(difficulty, DIFFICULTY_BIAS["normal"])
    for c in state.companies:
        is_player = c.name == PLAYER_COMPANY
        for p in c.products:
            if is_player:
                p.age = round(_clamp(p.age + bias["player_age"], 0.3, 7.0), 1)
                p.material_cost = round(max(1.0, p.material_cost * (1 + bias["player_cost"])), 2)
                p.labor_cost = round(max(0.5, p.labor_cost * (1 + bias["player_cost"])), 2)
            else:
                p.age = round(_clamp(p.age + bias["comp_age"], 0.3, 7.0), 1)
                p.awareness = round(_clamp(p.awareness + bias["comp_awareness"], 0.30, 0.95), 2)
                for key in list(p.accessibility.keys()):
                    p.accessibility[key] = round(
                        _clamp(p.accessibility[key] + bias["comp_awareness"], 0.30, 0.95), 2)
        if is_player:
            c.cash = round(max(0.0, c.cash * (1 + bias["player_cash"])), 0)
        _rebalance_company(c)


def generate_scenario(seed: int, difficulty: Optional[str] = None) -> GameState:
    """Deterministically perturb the base R0 state into a fresh scenario.

    The same (seed, difficulty) always yields the identical GameState, so Reset
    reproduces an identical puzzle. If `difficulty` is None it is derived from the
    seed. The result is NOT guaranteed playable; run it through the validator.
    """
    state = build_r0_state()
    rng = Random(seed)
    if difficulty is None:
        difficulty = DIFFICULTIES[seed % len(DIFFICULTIES)]

    # Segments: vary market growth and starting industry size (mechanics like
    # drift vectors, ideal offsets and buying weights are kept fixed — they are
    # the exam's structural rules, not the "puzzle").
    for seg in state.segments:
        seg.growth_rate = round(_clamp(seg.growth_rate + rng.uniform(-0.02, 0.02), 0.06, 0.20), 3)
        base_demand = state.industry_unit_demand.get(seg.name, 0)
        new_demand = max(500, int(_jitter(rng, base_demand, 0.10)))
        state.industry_unit_demand[seg.name] = new_demand
        state.industry_unit_sold[seg.name] = new_demand

    # Products + company books
    for c in state.companies:
        for p in c.products:
            seg = state.get_segment(p.primary_segment)
            _perturb_product(rng, p, seg)
        _perturb_company_financials(rng, c)

    # Difficulty bias (re-balances books internally)
    _apply_difficulty_bias(state, difficulty)

    return state


def build_scenario(scenario_id: str) -> GameState:
    """Build a GameState for a scenario id (see module docstring for id forms)."""
    seed, difficulty = parse_scenario_id(scenario_id)
    if seed is None:
        return build_r0_state()
    return generate_scenario(seed, difficulty)


if __name__ == "__main__":
    base = build_r0_state()
    scen = generate_scenario(42)
    print("=== scenario gen-42 vs base ===")
    for cb, cs in zip(base.companies, scen.companies):
        print(f"{cs.name}: cash ${cb.cash/1e6:.1f}M -> ${cs.cash/1e6:.1f}M, "
              f"RE ${cb.retained_earnings/1e6:.1f}M -> ${cs.retained_earnings/1e6:.1f}M")
    for sb, ss in zip(base.segments, scen.segments):
        print(f"{ss.name}: growth {sb.growth_rate:.0%} -> {ss.growth_rate:.0%}, "
              f"demand {base.industry_unit_demand[sb.name]} -> {scen.industry_unit_demand[ss.name]}")
    # Determinism check
    again = generate_scenario(42)
    print("deterministic:", scen.model_dump() == again.model_dump())
