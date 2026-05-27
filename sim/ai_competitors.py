"""
AI Competitor decision logic for Baldwin, Chester, Digby.

Strategies (per Capsim Professor Guide §15 Computer Company Strategies):
  - Baldwin: Niche Differentiator (High Tech: Nano + Elite focus)
  - Chester: Niche Cost Leader (Low Tech: Thrift + Core focus)
  - Digby: Broad Differentiator (all 4 segments)

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
    "Baldwin": {
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
    "Chester": {
        "focus_segments": ["Thrift", "Core"],
        "promo_budget_per_product": 1_100_000,
        "sales_budget_per_product": 900_000,
        "automation_target": {"Thrift": 9, "Core": 8, "Nano": 6, "Elite": 5},
        "price_strategy": "low",          # low pricing for volume
        "hr_recruit": 3500,
        "hr_training": 60,
        "tqm_spend_per_round": 4_000_000,
        "revise_aggressiveness": "low",   # save R&D, ride age
        "dividend_ratio": 0.30,
    },
    "Digby": {
        "focus_segments": ["Thrift", "Core", "Nano", "Elite"],
        "promo_budget_per_product": 1_200_000,
        "sales_budget_per_product": 1_000_000,
        "automation_target": {"Thrift": 8, "Core": 7, "Nano": 6, "Elite": 5},
        "price_strategy": "mid",
        "hr_recruit": 5000,
        "hr_training": 80,                # max HR
        "tqm_spend_per_round": 7_000_000,
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
    """Determine new price for AI competitor."""
    p_min = segment.price_min
    p_max = segment.price_max
    if strategy == "premium":
        return p_max - 1.0
    if strategy == "low":
        return p_min + 1.0
    return (p_min + p_max) / 2


def should_revise(product: Product, segment: Segment, aggressiveness: str,
                   round_num: int) -> bool:
    """Decide whether to revise a product this round."""
    # Always revise if very old or far from ideal
    from sim.engines.customer_score import position_distance
    dist = position_distance(product, segment)
    if aggressiveness == "high":
        return product.age > 1.5 or dist > 1.0
    if aggressiveness == "medium":
        return product.age > 2.5 or dist > 1.5
    return product.age > 3.5 or dist > 2.5  # low (Chester style — save money)


def baldwin_decisions(state: GameState) -> RoundDecision:
    return _generate_decisions(state, "Baldwin")


def chester_decisions(state: GameState) -> RoundDecision:
    return _generate_decisions(state, "Chester")


def digby_decisions(state: GameState) -> RoundDecision:
    return _generate_decisions(state, "Digby")


def _generate_decisions(state: GameState, company_name: str) -> RoundDecision:
    """Generate full round decisions for an AI competitor."""
    company = state.get_company(company_name)
    profile = STRATEGY_PROFILES[company_name]
    round_num = state.round_num + 1

    product_decisions = []
    for p in company.products:
        seg = state.get_segment(p.primary_segment)
        decision = ProductDecision(product_name=p.name)

        # Pricing
        decision.price = pricing_for_product(p, seg, profile["price_strategy"])

        # Marketing
        decision.promo_budget = profile["promo_budget_per_product"]
        decision.sales_budget = profile["sales_budget_per_product"]

        # Sales Forecast: predict based on last year + segment growth
        seg_growth = seg.growth_rate
        forecast = max(int(p.units_sold_last * (1 + seg_growth * 0.5)), 100)
        decision.forecast = forecast

        # Production: aim for 1.5x capacity (use 2nd shift)
        target_units = int(p.capacity_first_shift * 1.5)
        decision.production_schedule = target_units

        # R&D: revise to next year's ideal if worth it (SMART-CAP: limit to reachable in 330 days)
        if should_revise(p, seg, profile["revise_aggressiveness"], round_num):
            from math import sqrt as _sqrt
            target_pfmn, target_size = predicted_ideal_at_round(seg, 1)
            dist = _sqrt((target_pfmn - p.pfmn)**2 + (target_size - p.size)**2)
            tqm_factor = 1 + company.tqm.rd_cycle_time_reduction
            max_reachable = (270 / 180) / tqm_factor if tqm_factor > 0 else (270/180)
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

        # Automation upgrade (slow, +1 level if below target)
        target_auto = profile["automation_target"].get(p.primary_segment, 5)
        if p.automation < target_auto:
            decision.new_automation = min(p.automation + 1.0, target_auto)

        product_decisions.append(decision)

    # Finance: pay dividend ~ target ratio of last profit
    dividend_total = max(0, company.profit_last * profile["dividend_ratio"])
    div_per_share = (dividend_total / company.shares_outstanding
                     if company.shares_outstanding > 0 else 0)
    finance = FinanceDecision(dividend_per_share=round(div_per_share, 2))

    # Retire 13.5S2027 (high coupon, near maturity) if cash allows
    bonds_2027 = [b for b in company.bonds if b.year_due == 2027]
    if bonds_2027 and company.cash > 15_000_000:
        finance.retire_bond_early = [b.series for b in bonds_2027]

    # HR
    hr = HRDecision(
        recruit_spend=profile["hr_recruit"],
        training_hours=profile["hr_training"],
    )

    # TQM: allocate across top 4-6 initiatives
    tqm_total = profile["tqm_spend_per_round"]
    if round_num <= 2:
        # Heavy investment first 2 rounds
        tqm = TQMDecision(initiatives={
            "QFD Effort": min(1_500_000, tqm_total * 0.25),
            "CCE/6 Sigma": min(1_500_000, tqm_total * 0.25),
            "Vendor/JIT": min(1_500_000, tqm_total * 0.20),
            "CPI Systems": min(1_500_000, tqm_total * 0.15),
            "Concurrent Engineering": min(1_500_000, tqm_total * 0.15),
        })
    elif round_num == 3:
        # Maintenance
        tqm = TQMDecision(initiatives={
            "QFD Effort": 1_000_000,
            "CCE/6 Sigma": 1_000_000,
            "Channel Support Systems": 1_000_000,
            "Benchmarking": 1_000_000,
        })
    else:  # round 4
        # Minimal: just QFD
        tqm = TQMDecision(initiatives={"QFD Effort": 1_500_000})

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
    for ai_name in ["Baldwin", "Chester", "Digby"]:
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
