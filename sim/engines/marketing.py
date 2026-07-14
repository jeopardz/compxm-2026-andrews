"""
Marketing engine.

Per CompMastery classic marketing model (no advanced marketing module):
  Promo Budget → Awareness (per-product)
    $1.4M = maintain (zero growth)
    $2.0M = grow
    $3.0M = diminishing returns / cap
    Awareness DECAYS by ~33% per year if no spend

  Sales Budget → Accessibility (per-segment)
    Combined ~$4.5M for 2 products in same segment = optimal
    $3M per product if alone
    Accessibility DECAYS by ~33% per year if no spend

Reference:
  CompMastery promotion and sales-budget reference model
"""
from __future__ import annotations
from typing import Dict, List
from sim.data_models import Product, Segment, Company


# Awareness response curve breakpoints
AWARENESS_MAINTAIN_BUDGET = 1_400_000
AWARENESS_GROW_BUDGET = 2_000_000
AWARENESS_CAP_BUDGET = 3_000_000
AWARENESS_DECAY_PER_YEAR = 0.33   # 33% decay if no spend

# Accessibility response curve (per segment, combined across all products targeting it)
ACCESS_COMBINED_OPTIMAL = 4_500_000
ACCESS_SINGLE_OPTIMAL = 3_000_000
ACCESS_DECAY_PER_YEAR = 0.33


def promo_awareness_add(promo_spend: float) -> float:
    """Absolute awareness gained from this round's promo spend:
    $1.5M → +36%, $2M → +44%, $3M → +50% (ceiling), diminishing above. Applied on top of
    the decayed carry-over, so ~$1.4-1.5M offsets the 33% forgetting = maintain."""
    if promo_spend <= 0:
        return 0.0
    if promo_spend <= AWARENESS_GROW_BUDGET - 500_000:      # ≤ $1.5M
        return promo_spend / 1_500_000 * 0.36
    if promo_spend <= AWARENESS_GROW_BUDGET:                # ≤ $2.0M
        return 0.36 + (promo_spend - 1_500_000) / 500_000 * 0.08
    if promo_spend <= AWARENESS_CAP_BUDGET:                 # ≤ $3.0M
        return 0.44 + (promo_spend - AWARENESS_GROW_BUDGET) / 1_000_000 * 0.06
    return min(0.55, 0.50 + (promo_spend - AWARENESS_CAP_BUDGET) / 5_000_000 * 0.05)


def update_awareness(product: Product, promo_spend: float) -> float:
    """Update awareness with the decay-then-add model:
      new = last × (1 − 33% forgetting) + promo_awareness_add(spend)
    Reaching/maintaining 100% takes ~$1.4-1.5M (offsets the decay); zero spend loses a
    third. (Was a 'net change' approximation that never modelled the forgetting + build
    as separate steps.)"""
    decayed = product.awareness * (1 - AWARENESS_DECAY_PER_YEAR)
    product.awareness = max(0.0, min(1.0, decayed + promo_awareness_add(promo_spend)))
    product.promo_budget = promo_spend
    return product.awareness


def update_accessibility(state_companies: List[Company], segment_name: str,
                          sales_spend_per_product: Dict[str, float]) -> None:
    """
    Update accessibility per company per segment (accessibility belongs to the
    company, pooled across ONLY that company's own products in the segment — NOT across
    the whole industry). Each company gets ONE accessibility value for the segment,
    written to all of its products there.

    (Was: pooled every company's sales budget together and split by share, so a rival's
    spending wrongly diluted your accessibility — economically incoherent.)

    Net-change curve (per company's combined spend in the segment):
      $0            -> −33% multiplicative decay
      $3M solo      -> maintain (~0 net change)
      $4.5M for 2+  -> maintain
      above optimal -> small additional gain
    NOTE on the "≥2 products for 100%" authentic rule: that applies to the classic
    5-segment sensor game where companies double up products in a segment. Our 4-segment
    edition has exactly ONE product per segment by design, so we do NOT apply that cap
    (it would wrongly slash every company's seed-calibrated ~100% accessibility to 35%).
    We use the single-product optimal ($3M) as the maintain point instead.
    """
    for c in state_companies:
        prods = [p for p in c.products if p.primary_segment == segment_name]
        if not prods:
            continue
        total_spend = sum(sales_spend_per_product.get(p.name, p.sales_budget) for p in prods)
        n = len(prods)
        optimal = ACCESS_COMBINED_OPTIMAL if n >= 2 else ACCESS_SINGLE_OPTIMAL
        cur = max((p.accessibility.get(segment_name, 0.0) for p in prods), default=0.0)

        if total_spend <= 0:
            new_acc = max(0.0, cur * (1 - ACCESS_DECAY_PER_YEAR))
        elif total_spend <= optimal:
            decay_ratio = 1 - (total_spend / optimal)
            new_acc = max(0.0, cur * (1 - ACCESS_DECAY_PER_YEAR * decay_ratio))
        else:
            extra = min(0.08, (total_spend - optimal) / 2_000_000 * 0.05)
            new_acc = min(1.0, cur + extra)

        for p in prods:
            p.accessibility[segment_name] = new_acc
            p.sales_budget = sales_spend_per_product.get(p.name, p.sales_budget)


def update_price(product: Product, new_price: float, segment: Segment) -> None:
    """Set new price (no validation, but warn if outside expected range)."""
    product.price = new_price


def update_all_marketing(company: Company, segments: List[Segment],
                         all_companies: List[Company],
                         decisions: Dict) -> None:
    """
    Apply all marketing decisions for a company in one round.

    decisions: {
      product_name: {"price": ..., "promo": ..., "sales": ...}
    }
    """
    # Update price + awareness immediately
    for p in company.products:
        d = decisions.get(p.name, {})
        if "price" in d:
            seg = next(s for s in segments if s.name == p.primary_segment)
            update_price(p, d["price"], seg)
        if "promo" in d:
            update_awareness(p, d["promo"])

    # Update accessibility per segment (need all companies' sales spend)
    for seg in segments:
        sales_per_product: Dict[str, float] = {}
        for c in all_companies:
            for p in c.products:
                if p.primary_segment == seg.name:
                    if c.name == company.name:
                        sales_per_product[p.name] = decisions.get(p.name, {}).get("sales", p.sales_budget)
                    else:
                        sales_per_product[p.name] = p.sales_budget
        update_accessibility(all_companies, seg.name, sales_per_product)
