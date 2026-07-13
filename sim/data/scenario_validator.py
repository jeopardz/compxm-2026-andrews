"""
Scenario Validation Gauntlet.

A generated scenario must pass four gauntlets before it is fit to serve to a
paying user. Each gauntlet is a hard gate; a scenario that fails any one is
rejected (never served). The gauntlets, in order of cost:

  Gauntlet 1 — Structural: balance sheet identity holds, every product sits in
    its segment's rough-cut circle, prices/MTBF/capacity are sane, no NaN/negatives.
  Gauntlet 2 — Drift: after 4 years of drift every segment's ideal spot is still
    on the perceptual map (0..20 on both axes), so the puzzle stays solvable.
  Gauntlet 3 — Full playthrough: a competent baseline "player" (below) plays all
    4 rounds against the real AI competitors through the real engine. Must not
    crash, must not drive the player company to an emergency loan, must leave
    every segment with positive demand, and must keep every company solvent
    (stock >= $5).
  Gauntlet 4 — Fairness: the baseline player's average round BSC lands in a middle
    band (not trivially winnable, not unwinnable). The measured score also grades
    the scenario Easy / Normal / Hard.

`validate_scenario` returns a ValidationReport; `.ok` is True only if all four
pass. The baseline player deliberately mirrors the AI competitors' decision logic
(via the shared helpers in ai_competitors) so the playthrough reflects how the
engine actually rewards competent-but-not-optimal play.
"""
from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Optional

from sim.ai_competitors import (
    STRATEGY_PROFILES, predicted_ideal_at_round, pricing_for_product, should_revise,
)
from sim.data_models import (
    FinanceDecision, GameState, HRDecision, ProductDecision, RoundDecision, TQMDecision,
)
from sim.engines.customer_score import ROUGH_CUT_RADIUS, in_rough_cut
from sim.engines.production import automation_upgrade_cost
from sim.engines.round_engine import advance_round


PLAYER_COMPANY = "Apex"  # the company controlled by the human player

# Difficulty is graded on the baseline player's FINAL stock price, which has real
# dynamic range across scenarios (~$95-$175 after the Task-4 cost-realism changes:
# wage inflation, rating-tied debt rate, AP material withholding all add headwind).
# The round BSC total saturates, so it works only as a degeneracy floor, not the
# difficulty discriminator. Bands recalibrated 2026-07-11 to the post-Task-4 spread.
MIN_AVG_BSC = 40.0            # below this the baseline can't even function -> reject
STOCK_REJECT_LOW = 95.0      # calibrated to observed post-audit playthrough range
STOCK_REJECT_HIGH = 175.0    # reject genuinely trivial outliers, not unreachable values

# Difficulty grading thresholds on baseline final stock price (higher = easier).
DIFFICULTY_BANDS = [
    ("Hard", STOCK_REJECT_LOW, 125.0),
    ("Normal", 125.0, 155.0),
    ("Easy", 155.0, STOCK_REJECT_HIGH),
]

MAP_MIN, MAP_MAX = 0.0, 20.0


@dataclass
class ValidationReport:
    ok: bool = True
    difficulty: Optional[str] = None
    avg_bsc: Optional[float] = None
    final_stock: Optional[float] = None
    cumulative_profit: Optional[float] = None
    failures: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.ok = False
        self.failures.append(msg)


# ------------------------------------------------------------------
# Baseline "player" — a competent broad strategy for Gauntlet 3
# ------------------------------------------------------------------

_BASELINE_PROFILE = {
    "promo_budget_per_product": 1_400_000,
    "sales_budget_per_product": 1_100_000,
    "automation_target": {"Thrift": 8, "Core": 7, "Nano": 6, "Elite": 5},
    "price_strategy": "mid",
    "hr_recruit": 5000,
    "hr_training": 80,
    "tqm_spend_per_round": 6_000_000,
    "revise_aggressiveness": "medium",
    "dividend_ratio": 0.35,
}


def baseline_player_decisions(state: GameState, company_name: str = PLAYER_COMPANY) -> RoundDecision:
    """A reasonable, engine-consistent set of decisions for the player company.

    Mirrors the AI competitors' logic (shared helpers) so the playthrough reflects
    competent-but-not-perfect play — the standard we validate scenarios against.
    """
    company = state.get_company(company_name)
    profile = _BASELINE_PROFILE
    round_num = state.round_num + 1

    safety_reserve = max(8_000_000, company.sales_last * 0.12)
    available_cash = max(0, company.cash - safety_reserve)

    product_decisions = []
    for p in company.products:
        seg = state.get_segment(p.primary_segment)
        d = ProductDecision(product_name=p.name)
        d.price = pricing_for_product(p, seg, profile["price_strategy"])
        d.promo_budget = int(profile["promo_budget_per_product"])
        d.sales_budget = int(profile["sales_budget_per_product"])

        forecast = max(int(p.units_sold_last * (1 + seg.growth_rate * 0.5)), 100)
        d.forecast = forecast
        target_demand = int(p.units_sold_last * (1 + seg.growth_rate))
        d.production_schedule = max(100, int((target_demand - p.inventory) * 1.05))

        if should_revise(p, seg, profile["revise_aggressiveness"], round_num):
            target_pfmn, target_size = predicted_ideal_at_round(seg, 1)
            dist = math.sqrt((target_pfmn - p.pfmn) ** 2 + (target_size - p.size) ** 2)
            tqm_factor = 1 + company.tqm.rd_cycle_time_reduction
            max_reachable = (270 / 175) / tqm_factor if tqm_factor > 0 else (270 / 175)
            if dist > max_reachable and dist > 0:
                scale = max_reachable / dist
                d.new_pfmn = round(p.pfmn + (target_pfmn - p.pfmn) * scale, 1)
                d.new_size = round(p.size + (target_size - p.size) * scale, 1)
            else:
                d.new_pfmn, d.new_size = round(target_pfmn, 1), round(target_size, 1)
            d.new_mtbf = min(seg.mtbf_max, p.mtbf + 1000)

        target_auto = profile["automation_target"].get(p.primary_segment, 5)
        if p.automation < target_auto:
            est_cost = automation_upgrade_cost(p.capacity_first_shift, p.automation, p.automation + 1.0)
            if est_cost < available_cash * 0.30:
                d.new_automation = min(p.automation + 1.0, target_auto)
                available_cash -= est_cost

        product_decisions.append(d)

    dividend_total = max(0, company.profit_last * profile["dividend_ratio"])
    div_per_share = (dividend_total / company.shares_outstanding
                     if company.shares_outstanding > 0 else 0)
    finance = FinanceDecision(dividend_per_share=round(div_per_share, 2))

    bonds_2027 = [b for b in company.bonds if b.year_due == 2027]
    if bonds_2027 and round_num >= 2:
        bond_face = sum(b.face_value for b in bonds_2027)
        if available_cash > bond_face * 1.05 * 1.4:
            finance.retire_bond_early = [b.series for b in bonds_2027]
            available_cash -= bond_face * 1.05

    roll_over = company.current_debt
    buffer = int(company.sales_last * 0.03) if round_num <= 2 else 0
    finance.current_debt_borrow = int(roll_over + buffer)

    hr = HRDecision(recruit_spend=profile["hr_recruit"], training_hours=profile["hr_training"])

    per_init_cap = 1_500_000
    tqm_total = profile["tqm_spend_per_round"]
    tqm = TQMDecision(initiatives={
        "QFD Effort": min(per_init_cap, tqm_total * 0.25),
        "CCE/6 Sigma": min(per_init_cap, tqm_total * 0.25),
        "Vendor/JIT": min(per_init_cap, tqm_total * 0.20),
        "CPI Systems": min(per_init_cap, tqm_total * 0.15),
        "Concurrent Engineering": min(per_init_cap, tqm_total * 0.15),
    })

    return RoundDecision(round_num=round_num, products=product_decisions,
                         finance=finance, hr=hr, tqm=tqm)


# ------------------------------------------------------------------
# Gauntlets
# ------------------------------------------------------------------

def _is_finite_number(x) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(x)


def gauntlet_structural(state: GameState, report: ValidationReport) -> None:
    for c in state.companies:
        # Balance sheet identity
        net_plant = c.plant_value - c.accumulated_depreciation
        assets = c.cash + c.accounts_receivable + c.inventory_value + net_plant
        liab = c.accounts_payable + c.current_debt + sum(b.face_value for b in c.bonds)
        equity = c.common_stock + c.retained_earnings
        # Tolerance $50k (<0.05% of a ~$120M balance sheet). The hand-authored base
        # seed is itself ~$2k off from OCR rounding; a genuinely broken perturbation
        # would be off by millions.
        if not _is_finite_number(assets) or abs(assets - (liab + equity)) > 50_000.0:
            report.fail(f"{c.name}: balance sheet off by ${assets - (liab + equity):,.0f}")
        if net_plant <= 0:
            report.fail(f"{c.name}: non-positive net plant ${net_plant:,.0f}")
        if c.shares_outstanding <= 0:
            report.fail(f"{c.name}: non-positive shares")

        for p in c.products:
            seg = state.get_segment(p.primary_segment)
            for label, val in (("pfmn", p.pfmn), ("size", p.size), ("price", p.price),
                               ("material_cost", p.material_cost), ("labor_cost", p.labor_cost)):
                if not _is_finite_number(val) or val < 0:
                    report.fail(f"{p.name}: bad {label}={val}")
            if not in_rough_cut(p, seg):
                dx, dy = p.pfmn - seg.center_pfmn, p.size - seg.center_size
                report.fail(f"{p.name}: outside {seg.name} rough-cut "
                            f"(dist {math.hypot(dx, dy):.2f} > {ROUGH_CUT_RADIUS})")
            if not (seg.price_min <= p.price <= seg.price_max):
                report.fail(f"{p.name}: price ${p.price} outside {seg.name} band")
            if p.capacity_first_shift <= 0:
                report.fail(f"{p.name}: non-positive capacity")
            if p.mtbf <= 0:
                report.fail(f"{p.name}: non-positive MTBF")
            if not (1.0 <= p.automation <= 10.0):
                report.fail(f"{p.name}: automation {p.automation} out of 1..10")


def gauntlet_drift(state: GameState, report: ValidationReport, years: int = 4) -> None:
    for seg in state.segments:
        fut_pfmn, fut_size = predicted_ideal_at_round(seg, years)
        if not (MAP_MIN <= fut_pfmn <= MAP_MAX and MAP_MIN <= fut_size <= MAP_MAX):
            report.fail(f"{seg.name}: ideal spot drifts off-map after {years}y "
                        f"-> ({fut_pfmn:.1f}, {fut_size:.1f})")


def gauntlet_playthrough(state: GameState, report: ValidationReport) -> Optional[float]:
    """Play 4 rounds with the baseline player; return average round BSC total.

    Returns None if the playthrough itself is invalid (crash / emergency loan /
    dead segment / insolvent company). Mutates a COPY, never the passed-in state.
    """
    sim = deepcopy(state)
    bsc_totals: List[float] = []
    try:
        for _ in range(4):
            demand_before = dict(sim.industry_unit_demand)
            decisions = baseline_player_decisions(sim, PLAYER_COMPANY)
            result = advance_round(sim, decisions)
            bsc_totals.append(result["bsc"]["total"])

            player = sim.get_company(PLAYER_COMPANY)
            if player.emergency_loan > 0:
                report.fail(f"player took emergency loan in R{sim.round_num} "
                            f"(${player.emergency_loan:,.0f})")
                return None
            for seg_name, units in sim.industry_unit_demand.items():
                if units <= 0:
                    report.fail(f"{seg_name} demand collapsed to {units} in R{sim.round_num}")
                    return None
            for c in sim.companies:
                if c.stock_price < 5.0:
                    report.fail(f"{c.name} insolvent (stock ${c.stock_price:.2f}) in R{sim.round_num}")
                    return None
            _ = demand_before  # (kept for readability; growth handled by engine)
    except Exception as exc:  # noqa: BLE001 - any engine error means unplayable
        report.fail(f"playthrough crashed: {type(exc).__name__}: {exc}")
        return None

    player = sim.get_company(PLAYER_COMPANY)
    report.final_stock = round(player.stock_price, 2)
    report.cumulative_profit = round(player.cumulative_profit, 0)
    return sum(bsc_totals) / len(bsc_totals) if bsc_totals else None


def gauntlet_fairness(avg_bsc: Optional[float], final_stock: Optional[float],
                      report: ValidationReport) -> None:
    if avg_bsc is None or final_stock is None:
        report.fail("no baseline result produced (playthrough invalid)")
        return
    report.avg_bsc = round(avg_bsc, 1)
    if avg_bsc < MIN_AVG_BSC:
        report.fail(f"baseline BSC collapsed ({avg_bsc:.1f} < {MIN_AVG_BSC})")
        return
    if final_stock < STOCK_REJECT_LOW:
        report.fail(f"unfairly hard: baseline final stock ${final_stock:.0f} "
                    f"< ${STOCK_REJECT_LOW:.0f}")
        return
    if final_stock > STOCK_REJECT_HIGH:
        report.fail(f"trivial: baseline final stock ${final_stock:.0f} "
                    f"> ${STOCK_REJECT_HIGH:.0f}")
        return
    for label, lo, hi in DIFFICULTY_BANDS:
        if lo <= final_stock < hi:
            report.difficulty = label
            break
    report.difficulty = report.difficulty or "Normal"


def validate_scenario(state: GameState) -> ValidationReport:
    """Run all four gauntlets. `.ok` is True only if the scenario passes every one."""
    report = ValidationReport()

    gauntlet_structural(state, report)
    gauntlet_drift(state, report)
    if not report.ok:
        # Structural/drift failures make the playthrough meaningless — stop early.
        return report

    avg_bsc = gauntlet_playthrough(state, report)
    if not report.ok:
        return report

    gauntlet_fairness(avg_bsc, report.final_stock, report)
    return report


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    from sim.data.scenarios import generate_scenario

    print("=== base (exam-a) ===")
    rep = validate_scenario(build_r0_state())
    print(f"ok={rep.ok} difficulty={rep.difficulty} avg_bsc={rep.avg_bsc} "
          f"stock=${rep.final_stock} cumprofit=${(rep.cumulative_profit or 0)/1e6:.1f}M")
    for f in rep.failures:
        print("  FAIL:", f)

    passed = 0
    total = 0
    for difficulty in ("easy", "normal", "hard"):
        print(f"\n--- target difficulty: {difficulty} ---")
        for seed in range(1, 9):
            total += 1
            rep = validate_scenario(generate_scenario(seed, difficulty))
            status = rep.difficulty if rep.ok else "REJECT: " + (rep.failures[0] if rep.failures else "?")
            print(f"seed {seed:3d}: ok={rep.ok!s:5} avg_bsc={rep.avg_bsc} "
                  f"stock=${rep.final_stock} -> {status}")
            passed += int(rep.ok)
    print(f"\n{passed}/{total} seeds passed the gauntlet")
