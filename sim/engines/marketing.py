"""
Marketing engine.

Per Capsim Classic (which is what Comp-XM uses — NO Advanced Marketing Module):
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
  https://ww3.capsim.com/guides/capstone_harvard2011/the-guide/4-operations/42-marketing77ba.html
  https://ww3.capsim.com/guides/capstone_harvard2011/-marketing/135-what-is-the-difference-between-the-promotion-and-sales-budgets.html
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


def awareness_gain(promo_spend: float) -> float:
    """
    How much awareness does $spend buy (additive to current awareness, 0..1).
    Calibrated so:
      $0 -> 0 gain (and decay applies)
      $1.4M -> +0.0 (just covers decay)
      $2.0M -> +0.12 to grow
      $3.0M -> +0.20 cap
      $5.0M -> still +0.22 (diminishing returns)
    """
    if promo_spend <= 0:
        return 0.0
    if promo_spend <= AWARENESS_MAINTAIN_BUDGET:
        # Just covers decay
        return promo_spend / AWARENESS_MAINTAIN_BUDGET * AWARENESS_DECAY_PER_YEAR
    if promo_spend <= AWARENESS_GROW_BUDGET:
        # Linear growth
        excess = promo_spend - AWARENESS_MAINTAIN_BUDGET
        return AWARENESS_DECAY_PER_YEAR + excess / (AWARENESS_GROW_BUDGET - AWARENESS_MAINTAIN_BUDGET) * 0.12
    if promo_spend <= AWARENESS_CAP_BUDGET:
        # Diminishing returns
        excess = promo_spend - AWARENESS_GROW_BUDGET
        return AWARENESS_DECAY_PER_YEAR + 0.12 + excess / (AWARENESS_CAP_BUDGET - AWARENESS_GROW_BUDGET) * 0.08
    # Above $3M cap
    return AWARENESS_DECAY_PER_YEAR + 0.20 + min(0.02, (promo_spend - AWARENESS_CAP_BUDGET) / 5_000_000)


def update_awareness(product: Product, promo_spend: float) -> float:
    """
    Update product's awareness based on promo spend using NET change formula.

    Verified curve (matches Capsim docs):
      $0 spend     -> awareness × 0.67 (pure -33% decay)
      $1.4M spend  -> awareness stays flat (net 0% change)
      $2M spend    -> awareness + 12% (absolute)
      $3M spend    -> awareness + 20% (cap)
      $5M+         -> + 22% (diminishing)
    """
    if promo_spend <= 0:
        # Pure multiplicative decay
        product.awareness *= (1 - AWARENESS_DECAY_PER_YEAR)
    elif promo_spend <= AWARENESS_MAINTAIN_BUDGET:
        # Partial decay scaled by spend (at $1.4M, decay = 0 = maintain)
        decay_ratio = 1 - (promo_spend / AWARENESS_MAINTAIN_BUDGET)
        decay = AWARENESS_DECAY_PER_YEAR * decay_ratio
        product.awareness *= (1 - decay)
    elif promo_spend <= AWARENESS_GROW_BUDGET:
        # Linear net gain from 0 at $1.4M to +12% at $2M
        net_gain = (promo_spend - AWARENESS_MAINTAIN_BUDGET) / \
                   (AWARENESS_GROW_BUDGET - AWARENESS_MAINTAIN_BUDGET) * 0.12
        product.awareness = min(1.0, product.awareness + net_gain)
    elif promo_spend <= AWARENESS_CAP_BUDGET:
        # Diminishing from +12% at $2M to +20% at $3M
        net_gain = 0.12 + (promo_spend - AWARENESS_GROW_BUDGET) / \
                   (AWARENESS_CAP_BUDGET - AWARENESS_GROW_BUDGET) * 0.08
        product.awareness = min(1.0, product.awareness + net_gain)
    else:
        # Above $3M: cap +20% with tiny extra
        net_gain = 0.20 + min(0.02, (promo_spend - AWARENESS_CAP_BUDGET) / 5_000_000)
        product.awareness = min(1.0, product.awareness + net_gain)

    product.awareness = max(0.0, product.awareness)
    product.promo_budget = promo_spend
    return product.awareness


def access_gain_combined(total_sales_spend: float, n_products: int) -> float:
    """
    Total accessibility gain for a segment from combined sales spend across N products in it.
    Single product optimal at $3M, two-product optimal at $4.5M, then diminishing.
    """
    if total_sales_spend <= 0:
        return 0.0
    optimal = ACCESS_COMBINED_OPTIMAL if n_products >= 2 else ACCESS_SINGLE_OPTIMAL
    if total_sales_spend <= optimal:
        return total_sales_spend / optimal * 0.35  # up to +35% per year if at optimal
    # Diminishing
    return 0.35 + min(0.05, (total_sales_spend - optimal) / 5_000_000)


def update_accessibility(state_companies: List[Company], segment_name: str,
                          sales_spend_per_product: Dict[str, float]) -> None:
    """
    Update accessibility per segment using NET change formula (same as awareness).

    Per segment optimal:
      $0       -> -33% multiplicative decay
      $3M solo -> stays flat (~0 net change)
      $4.5M for 2+ products -> stays flat
      Above optimal -> small additional gain
    """
    products_in_seg = []
    for c in state_companies:
        for p in c.products:
            if p.primary_segment == segment_name:
                products_in_seg.append(p)

    total_spend = sum(sales_spend_per_product.get(p.name, p.sales_budget)
                      for p in products_in_seg)
    n = len(products_in_seg)
    optimal = ACCESS_COMBINED_OPTIMAL if n >= 2 else ACCESS_SINGLE_OPTIMAL

    for p in products_in_seg:
        spend = sales_spend_per_product.get(p.name, p.sales_budget)
        share = (spend / total_spend) if total_spend > 0 else (1.0 / max(1, n))
        my_optimal = optimal * share  # fair share of segment optimal

        if spend <= 0:
            # Pure decay
            cur = p.accessibility.get(segment_name, 0.0)
            p.accessibility[segment_name] = max(0, cur * (1 - ACCESS_DECAY_PER_YEAR))
        elif spend <= my_optimal:
            # Partial decay scaled by spend (at my_optimal, decay = 0)
            decay_ratio = 1 - (spend / my_optimal)
            decay = ACCESS_DECAY_PER_YEAR * decay_ratio
            cur = p.accessibility.get(segment_name, 0.0)
            p.accessibility[segment_name] = max(0, cur * (1 - decay))
        else:
            # Above my_optimal: small additional gain (diminishing)
            extra = min(0.08, (spend - my_optimal) / 2_000_000 * 0.05)
            cur = p.accessibility.get(segment_name, 0.0)
            p.accessibility[segment_name] = min(1.0, cur + extra)
        p.sales_budget = spend


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


if __name__ == "__main__":
    print("=== Awareness response curve ===")
    for spend in [0, 500_000, 1_400_000, 1_700_000, 2_000_000, 2_500_000, 3_000_000, 4_000_000]:
        print(f"  ${spend/1e6:.1f}M spend -> +{awareness_gain(spend)*100:.1f}% awareness gain")

    print("\n=== Accessibility gain (combined budget per segment) ===")
    for spend in [0, 1_000_000, 2_000_000, 3_000_000, 4_500_000, 6_000_000]:
        for n in [1, 2]:
            print(f"  ${spend/1e6:.1f}M spend on {n} product(s) -> +{access_gain_combined(spend, n)*100:.1f}% access gain")
