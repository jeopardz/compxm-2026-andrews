"""
AI Competitor decision logic for Borealis, Crestline, Dynamo.

Strategies (per CompMastery computer-company strategy model):
  - Borealis: Niche Differentiator (High Tech: Nano + Elite focus)
  - Crestline: Niche Cost Leader (Low Tech: Thrift + Core focus)
  - Dynamo: Broad Differentiator (all 4 segments)

Each AI generates per-round decisions (R&D, Marketing, Production, HR, TQM, Finance)
based on its strategic profile and current state.
"""
from __future__ import annotations
from typing import List, Dict
from sim.data_models import (
    Company, Product, Segment, GameState, RoundDecision,
    ProductDecision, FinanceDecision, HRDecision, TQMDecision,
)


# Strategy profiles
STRATEGY_PROFILES = {
    "Borealis": {
        "focus_segments": ["Nano", "Elite"],
        "promo_budget_per_product": 1_500_000,
        "sales_budget_per_product": 1_300_000,
        "automation_target": {"Thrift": 7, "Core": 7, "Nano": 5, "Elite": 5},
        "price_strategy": "premium",      # high-end pricing
        "hr_recruit": 2500,
        "hr_training": 60,
        "tqm_spend_per_round": 6_000_000,
        "revise_aggressiveness": "high",
        "dividend_ratio": 0.50,
    },
    "Crestline": {
        "focus_segments": ["Thrift", "Core"],
        "promo_budget_per_product": 1_600_000,
        "sales_budget_per_product": 1_600_000,
        "automation_target": {"Thrift": 9, "Core": 8, "Nano": 6, "Elite": 5},
        "price_strategy": "premium",      # monetize its cost advantage; avoid EPS starvation
        "hr_recruit": 3500,
        "hr_training": 60,
        "tqm_spend_per_round": 7_000_000,
        "revise_aggressiveness": "medium",
        "dividend_ratio": 0.65,
    },
    "Dynamo": {
        "focus_segments": ["Thrift", "Core", "Nano", "Elite"],
        "promo_budget_per_product": 1_200_000,
        "sales_budget_per_product": 1_000_000,
        "automation_target": {"Thrift": 8, "Core": 7, "Nano": 6, "Elite": 5},
        "price_strategy": "mid",
        "hr_recruit": 5000,
        "hr_training": 80,                # max HR
        "tqm_spend_per_round": 5_000_000,  # was 7M — over-committed R1 cash with 4 products
        "revise_aggressiveness": "medium",
        "dividend_ratio": 0.40,
    },
}


def predicted_ideal_at_round(seg: Segment, rounds_ahead: int) -> tuple[float, float]:
    """Predict where ideal spot will be after `rounds_ahead` years of drift."""
    fut_pfmn = seg.center_pfmn + seg.drift_pfmn * rounds_ahead + seg.ideal_offset_pfmn
    fut_size = seg.center_size + seg.drift_size * rounds_ahead + seg.ideal_offset_size
    return fut_pfmn, fut_size


def pricing_for_product(product: Product, segment: Segment, strategy: str) -> float:
    """Determine new price for AI competitor.

    Strategy-driven but margin-safe: a low-cost leader prices near the floor (only
    as low as keeps a ~$5 unit margin), a differentiator holds the top of the range.
    Never prices so low that contribution margin collapses, nor above the range max.
    """
    p_min = segment.price_min
    p_max = segment.price_max
    mid = (p_min + p_max) / 2
    unit_cost = product.material_cost + product.labor_cost
    margin_floor = unit_cost + 5.0   # keep at least ~$5/unit contribution
    if strategy == "premium":
        # Hold the high end (differentiation justifies it)
        return round(min(p_max - 1.0, max(mid + 2.0, product.price - 1.0)), 2)
    if strategy == "low":
        # Cost leader: stay in the low-competitive zone but DON'T slash to the floor —
        # its automation gives a cost edge, so it should hold a healthy margin rather
        # than give it away. Target ~lower-third of range, floored by margin safety.
        return round(max(margin_floor + 1.5, mid - 2.5), 2)
    # mid / broad
    return round(max(margin_floor, min(p_max - 1.0, mid)), 2)


def should_revise(product: Product, segment: Segment, aggressiveness: str,
                   round_num: int) -> bool:
    """Decide whether to revise a product this round.

    CRITICAL: measure distance to the FUTURE (end-of-round) ideal spot, because the
    product will be SOLD/scored against the DRIFTED segment — not where the segment
    sits at decision time. Using the current (pre-drift) ideal made the AI decide
    "close enough, don't revise", then the segment drifted away and the product lost
    share and overproduced. Also use age+1 (the product ages over the year).

    Segment-aware: Nano/Elite (ideal age 1.0/0.0, heavy age weight) get revised
    almost every round; Thrift/Core can run a little older.
    """
    from math import sqrt
    fut_pfmn, fut_size = predicted_ideal_at_round(segment, 1)
    dist = sqrt((fut_pfmn - product.pfmn) ** 2 + (fut_size - product.size) ** 2)
    year_end_age = product.age + 1.0
    if aggressiveness == "high":      # Borealis — high-tech, keep Nano/Elite fresh
        age_tol, dist_tol = 0.8, 0.8
    elif aggressiveness == "medium":  # Dynamo — broad
        age_tol, dist_tol = 1.2, 1.0
    else:                              # low — Crestline cost leader: let age run, track position
        age_tol, dist_tol = 2.0, 1.0
    return year_end_age > segment.ideal_age + age_tol or dist > dist_tol


def borealis_decisions(state: GameState) -> RoundDecision:
    return _generate_decisions(state, "Borealis")


def crestline_decisions(state: GameState) -> RoundDecision:
    return _generate_decisions(state, "Crestline")


def dynamo_decisions(state: GameState) -> RoundDecision:
    return _generate_decisions(state, "Dynamo")


def _generate_decisions(state: GameState, company_name: str) -> RoundDecision:
    """Generate full round decisions for an AI competitor.

    Affordability-aware: scales discretionary spend (marketing, TQM, automation,
    bond retirement) down when cash is tight so AIs don't crash to emergency loans
    in R1. Previously Crestline spent $16M on automation + $11M bond + $8M marketing
    on $32M cash → bankrupt. Same for Borealis ($19M cash).
    """
    from sim.engines.production import automation_upgrade_cost
    company = state.get_company(company_name)
    profile = STRATEGY_PROFILES[company_name]
    round_num = state.round_num + 1

    # ---- Affordability budget ----
    # available_cash = cash we can spend on CAPEX / bond-retire / dividend without
    # risking an emergency loan. Operating expenses (marketing, TQM, HR) are funded
    # by revenue during the year, so they are NOT scaled down here — starving them
    # to hoard cash is a death spiral (TQM/marketing are investments that pay back).
    # We only gate the genuine cash-out items (automation, capacity, bond retire).
    safety_reserve = max(8_000_000, company.sales_last * 0.12)
    available_cash = max(0, company.cash - safety_reserve)

    product_decisions = []
    for p in company.products:
        seg = state.get_segment(p.primary_segment)
        decision = ProductDecision(product_name=p.name)

        # Pricing
        decision.price = pricing_for_product(p, seg, profile["price_strategy"])

        # Marketing — keep at full profile (operating expense funded by revenue;
        # cutting it would decay awareness/accessibility = lose demand)
        decision.promo_budget = int(profile["promo_budget_per_product"])
        decision.sales_budget = int(profile["sales_budget_per_product"])

        # Sales Forecast: predict based on last year + segment growth
        seg_growth = seg.growth_rate
        forecast = max(int(p.units_sold_last * (1 + seg_growth * 0.5)), 100)
        decision.forecast = forecast

        # Production: use CompMastery playbook formula = (forecast - inventory) × 1.05
        # This is the SAME formula UI defaults to — avoids overproduction that
        # was killing AI profitability via wasted material/labor + inventory carry
        target_demand = int(p.units_sold_last * (1 + seg.growth_rate))
        target_units = max(100, int((target_demand - p.inventory) * 1.05))
        decision.production_schedule = target_units

        # R&D: revise to next year's ideal if worth it (SMART-CAP: limit to reachable in 330 days)
        if should_revise(p, seg, profile["revise_aggressiveness"], round_num):
            from math import sqrt as _sqrt
            target_pfmn, target_size = predicted_ideal_at_round(seg, 1)
            dist = _sqrt((target_pfmn - p.pfmn)**2 + (target_size - p.size)**2)
            tqm_factor = 1 + company.tqm.rd_cycle_time_reduction
            max_reachable = (270 / 175) / tqm_factor if tqm_factor > 0 else (270/175)
            if dist > max_reachable and dist > 0:
                # Scale toward ideal but limit to reachable distance
                scale = max_reachable / dist
                new_pfmn = round(p.pfmn + (target_pfmn - p.pfmn) * scale, 1)
                new_size = round(p.size + (target_size - p.size) * scale, 1)
            else:
                new_pfmn, new_size = round(target_pfmn, 1), round(target_size, 1)
            decision.new_pfmn = new_pfmn
            decision.new_size = new_size
            target_mtbf = min(seg.mtbf_max, p.mtbf + 1000)
            decision.new_mtbf = target_mtbf

        # Automation upgrade — only if affordable. Cost = cap_units * $4M/level
        target_auto = profile["automation_target"].get(p.primary_segment, 5)
        if p.automation < target_auto:
            est_cost = automation_upgrade_cost(p.capacity_first_shift, p.automation, p.automation + 1.0)
            # Only upgrade if cost < 30% of available_cash (one product at a time)
            if est_cost < available_cash * 0.30:
                decision.new_automation = min(p.automation + 1.0, target_auto)
                available_cash -= est_cost  # decrement so next product can't also upgrade

        product_decisions.append(decision)

    # Finance: pay dividend ~ target ratio of last profit
    dividend_total = max(0, company.profit_last * profile["dividend_ratio"])
    div_per_share = (dividend_total / company.shares_outstanding
                     if company.shares_outstanding > 0 else 0)
    finance = FinanceDecision(dividend_per_share=round(div_per_share, 2))

    # Retire 13.5S2027 ONLY from leftover CAPEX cash (available_cash after automation),
    # and never in R1 (cash is committed to automation + ramping operations).
    # BUG FIX: previously gated on stale full company.cash, so Crestline retired an
    # $11.5M bond in R1 on top of automation + operating spend → emergency loan.
    bonds_2027 = [b for b in company.bonds if b.year_due == 2027]
    if bonds_2027 and round_num >= 2:
        bond_face = sum(b.face_value for b in bonds_2027)
        retire_cash_out = bond_face * 1.05  # face + ~1.5% fee + price premium cushion
        if available_cash > retire_cash_out * 1.4:
            finance.retire_bond_early = [b.series for b in bonds_2027]
            available_cash -= retire_cash_out

    # Current debt: the engine repays ALL prior current debt each year, so an AI
    # must ROLL it over (reborrow) or it bleeds that cash (Dynamo starts with $25.5M).
    # Roll the existing balance, plus a small working-capital buffer in early rounds.
    roll_over = company.current_debt
    buffer = int(company.sales_last * 0.03) if round_num <= 2 else 0
    finance.current_debt_borrow = int(roll_over + buffer)

    # HR — operating expense; keep full (recruit cost is only on new hires, training is cheap)
    hr = HRDecision(
        recruit_spend=profile["hr_recruit"],
        training_hours=profile["hr_training"],
    )

    # TQM: full profile budget (operating expense; investment that compounds —
    # do NOT scale to hoard cash). Per-initiative $1.5M/round cap still applies.
    tqm_total = profile["tqm_spend_per_round"]
    per_init_cap = 1_500_000  # $1.5M cap per initiative per round
    if round_num <= 2:
        tqm = TQMDecision(initiatives={
            "QFD Effort": min(per_init_cap, tqm_total * 0.25),
            "CCE/6 Sigma": min(per_init_cap, tqm_total * 0.25),
            "Vendor/JIT": min(per_init_cap, tqm_total * 0.20),
            "CPI Systems": min(per_init_cap, tqm_total * 0.15),
            "Concurrent Engineering": min(per_init_cap, tqm_total * 0.15),
        })
    elif round_num == 3:
        tqm = TQMDecision(initiatives={
            "QFD Effort": min(per_init_cap, tqm_total * 0.30),
            "CCE/6 Sigma": min(per_init_cap, tqm_total * 0.30),
            "Channel Support Systems": min(per_init_cap, tqm_total * 0.20),
            "Benchmarking": min(per_init_cap, tqm_total * 0.20),
        })
    else:  # round 4
        tqm = TQMDecision(initiatives={"QFD Effort": min(per_init_cap, tqm_total * 0.5)})

    return RoundDecision(
        round_num=round_num,
        products=product_decisions,
        finance=finance,
        hr=hr,
        tqm=tqm,
    )


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    for ai_name in ["Borealis", "Crestline", "Dynamo"]:
        decs = _generate_decisions(state, ai_name)
        print(f"\n=== {ai_name} R1 decisions ===")
        for pd in decs.products:
            print(f"  {pd.product_name}: price=${pd.price:.2f}, "
                  f"revise={pd.new_pfmn is not None}, "
                  f"prod={pd.production_schedule}, "
                  f"auto={pd.new_automation}")
        print(f"  Finance: div ${decs.finance.dividend_per_share:.2f}/share, "
              f"retire {decs.finance.retire_bond_early}")
        print(f"  HR: recruit ${decs.hr.recruit_spend}, train {decs.hr.training_hours}hr")
        print(f"  TQM: ${sum(decs.tqm.initiatives.values())/1e6:.1f}M across {len(decs.tqm.initiatives)} initiatives")
