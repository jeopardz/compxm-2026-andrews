"""
R&D engine.

Per Capsim:
  - R&D project time = base_time + distance_to_new_position × time_per_unit_distance
    Roughly: 1.0 year for short revise (≤0.5 units), up to 3 years for big move
  - Age halves on revise (e.g., age 5.0 -> 2.5)
  - Cost = $1M base + position move cost + MTBF change cost
  - MTBF can move up to +/-5000 units per project
  - Cannot launch new products in Comp-XM (only modify existing 4)

Reference: Capstone User Guide §4.1 R&D
"""
from __future__ import annotations
from math import sqrt
from datetime import date, timedelta
from typing import Optional, Dict
from sim.data_models import Product


BASE_RD_COST = 1_000_000.0          # $ minimum per project
COST_PER_POSITION_UNIT = 500_000.0  # $ per unit of (pfmn or size) change
COST_PER_MTBF_1000 = 5000.0         # $ per 1000 MTBF unit change
BASE_PROJECT_DAYS = 45              # ~1.5 month floor (MTBF-only / tiny move)
DAYS_PER_DISTANCE_UNIT = 175        # ~5.75 months per unit distance


def rd_distance(p: Product, new_pfmn: float, new_size: float) -> float:
    """Euclidean distance from current position to new target."""
    return sqrt((new_pfmn - p.pfmn) ** 2 + (new_size - p.size) ** 2)


def rd_project_days(p: Product, new_pfmn: float, new_size: float,
                    rd_cycle_reduction: float = 0.0) -> int:
    """
    Estimated project duration in days. TQM R&D cycle time reduction shrinks this.

    rd_cycle_reduction: fraction (e.g., 0.20 = 20% faster from TQM)
    """
    dist = rd_distance(p, new_pfmn, new_size)
    # Calibrated to real Comp-XM revision dates (cheatsheet R1): ~175 days per unit
    # of position distance — dist 0.5≈3mo, 1.0≈6mo, 1.4≈8mo, 1.84≈10mo (completes
    # in-year), min ~45 days. Was 60 + 180×dist which ran ~40% too slow, pushing a
    # normal 1.8-unit revise to 391 days (spilling into next year and failing the
    # "revise toward this round's ideal spot to win this round" strategy).
    days = max(BASE_PROJECT_DAYS, dist * DAYS_PER_DISTANCE_UNIT)
    days *= (1 - rd_cycle_reduction)
    return int(round(days))


def rd_completion_date(start_date: str, project_days: int) -> str:
    """Returns ISO date string when project completes."""
    sd = date.fromisoformat(start_date)
    cd = sd + timedelta(days=project_days)
    return cd.isoformat()


def rd_project_cost(p: Product,
                    new_pfmn: float, new_size: float,
                    new_mtbf: int) -> float:
    """Total cost of one R&D project."""
    cost = BASE_RD_COST
    cost += rd_distance(p, new_pfmn, new_size) * COST_PER_POSITION_UNIT
    cost += abs(new_mtbf - p.mtbf) / 1000 * COST_PER_MTBF_1000
    return cost


def apply_revise(p: Product,
                 new_pfmn: float, new_size: float, new_mtbf: int,
                 round_start_date: str = "2026-01-01",
                 rd_cycle_reduction: float = 0.0) -> Dict:
    """
    Apply an R&D revise. Updates product in place.

    On revise:
      - Position moves to (new_pfmn, new_size) at completion
      - MTBF moves to new_mtbf
      - Age halves (Capsim mechanic: revising = "refreshing" the product)

    Returns dict with completion details.
    """
    dist = rd_distance(p, new_pfmn, new_size)
    days = rd_project_days(p, new_pfmn, new_size, rd_cycle_reduction)
    cost = rd_project_cost(p, new_pfmn, new_size, new_mtbf)
    completion = rd_completion_date(round_start_date, days)

    p.rd_target_pfmn = new_pfmn
    p.rd_target_size = new_size
    p.rd_target_mtbf = new_mtbf
    p.rd_completion_date = completion

    return {
        "product": p.name,
        "distance": dist,
        "project_days": days,
        "completion_date": completion,
        "cost": cost,
        "old_pos": (p.pfmn, p.size),
        "new_pos": (new_pfmn, new_size),
        "mtbf_change": new_mtbf - p.mtbf,
    }


def end_of_year_apply_completed_projects(p: Product, year_end_date: str = "2026-12-31",
                                          year_start_date: str = "2026-01-01") -> bool:
    """
    At year-end, finalize any R&D project that completed during the year.

    Capsim age mechanics (CORRECTED):
      1. Product ages during R&D from start-of-year to completion
      2. At completion, age HALVES
      3. After completion, ages normally until year-end

    Formula:
      months_during_rd = (completion_date - year_start) / 30.44
      months_after = (year_end - completion_date) / 30.44
      age_at_completion = old_age + months_during_rd / 12
      new_age = age_at_completion / 2 + months_after / 12

    Returns True if a project completed.
    """
    if not p.rd_completion_date:
        return False
    if p.rd_completion_date <= year_end_date:
        from datetime import date
        cd = date.fromisoformat(p.rd_completion_date)
        ys = date.fromisoformat(year_start_date)
        ye = date.fromisoformat(year_end_date)

        months_during_rd = max(0, (cd - ys).days) / 30.44
        months_after = max(0, (ye - cd).days) / 30.44

        old_age = p.age
        age_at_completion = old_age + months_during_rd / 12.0
        new_age = age_at_completion / 2.0 + months_after / 12.0

        # Apply revision: position, MTBF, age, revision date
        p.pfmn = p.rd_target_pfmn
        p.size = p.rd_target_size
        p.mtbf = p.rd_target_mtbf
        p.revision_date = p.rd_completion_date
        p.age = round(new_age, 2)

        # Clear R&D in-progress fields
        p.rd_target_pfmn = None
        p.rd_target_size = None
        p.rd_target_mtbf = None
        p.rd_completion_date = None
        return True
    return False


def advance_age_one_year(p: Product) -> None:
    """At year-end, if no revision completed, age increases by 1 year."""
    p.age = round(p.age + 1.0, 2)


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    andrews = state.get_company("Andrews")
    print("=== R&D demo: Andrews R1 revisions ===\n")

    # Attic: critical revise (age 5.1, position behind Thrift)
    attic = next(p for p in andrews.products if p.name == "Attic")
    print(f"Attic before: pos ({attic.pfmn},{attic.size}) age {attic.age} MTBF {attic.mtbf}")
    result = apply_revise(attic, 6.2, 13.8, 20000, "2026-01-01")
    print(f"  Revise to (6.2,13.8): distance {result['distance']:.2f}, "
          f"days {result['project_days']}, cost ${result['cost']/1e6:.2f}M, "
          f"completes {result['completion_date']}")

    # Year-end: apply completed project
    completed = end_of_year_apply_completed_projects(attic, "2026-12-31")
    print(f"  Year-end finalize: completed={completed}, "
          f"new pos ({attic.pfmn},{attic.size}) new age {attic.age}")

    # Art: move to keep up with Nano drift
    art = next(p for p in andrews.products if p.name == "Art")
    print(f"\nArt before: pos ({art.pfmn},{art.size}) age {art.age}")
    result = apply_revise(art, 10.5, 7.2, 24000, "2026-01-01")
    print(f"  Revise to Nano R1 ideal (10.5,7.2): distance {result['distance']:.2f}, "
          f"days {result['project_days']}, cost ${result['cost']/1e6:.2f}M")
