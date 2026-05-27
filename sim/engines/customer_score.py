"""
Customer Survey Score engine.

Per Capsim official guide:
  Score per criterion = 0-100 based on how close product is to ideal.
  Weighted Score = Σ (criterion_score × criterion_weight)
  Net Score = Weighted × Awareness × Accessibility × Age_curve × MTBF_curve × Position_curve

For each segment, customers weight 4 criteria differently:
  - Price (linear within range, 0 outside)
  - Age (peak at ideal_age, drops off)
  - MTBF (linear within range, 0 below min, plateau above max)
  - Position (distance from ideal spot in 2D, fine-cut circle)

Reference:
  https://ww3.capsim.com/guides/capstone_harvard2011/-reports/162-how-is-the-customer-survey-score-calculatedbc9c.html
"""
from __future__ import annotations
from math import sqrt
from sim.data_models import Product, Segment


# Fine-cut circle radius (preferred-spot scoring zone). Outside this, score drops to 0.
FINE_CUT_RADIUS = 2.5

# Rough-cut circle radius (segment boundary). Outside, product gets 0 for that segment.
ROUGH_CUT_RADIUS = 4.0


def price_score(price: float, seg: Segment) -> float:
    """
    Score 0-100 based on price within segment's expected range.
    Customers prefer the LOW end of the price range.
    Outside range → 0.
    """
    if price < seg.price_min or price > seg.price_max:
        return 0.0
    # Score 100 at min, decreasing linearly to ~0 at max
    range_size = seg.price_max - seg.price_min
    if range_size <= 0:
        return 50.0
    # Linear: best (100) at min, worst (~10) at max
    normalized = (price - seg.price_min) / range_size  # 0 at min, 1 at max
    return 100.0 * (1.0 - normalized * 0.9)


def age_score(age: float, seg: Segment) -> float:
    """
    Score 0-100 based on age vs segment's ideal age.
    Symmetric around ideal_age. Each year of deviation drops score.

    Capsim "ideal age" rule: score drops ~10 points per 0.5 year deviation,
    floor at 0. We model as triangular: peak at ideal, half-width ~ ideal_age + 1.5yr.
    """
    deviation = abs(age - seg.ideal_age)
    half_width = max(seg.ideal_age + 1.5, 2.0)  # at least 2yr tolerance
    if deviation >= half_width:
        return 0.0
    return 100.0 * (1.0 - deviation / half_width)


def mtbf_score(mtbf: int, seg: Segment) -> float:
    """
    Score 0-100 based on MTBF (Mean Time Between Failure).
    Below min → 0. Within range → linear (low end ≈ 70, high end = 100).
    Above max → plateau at 100 (no extra reward, but no penalty).
    """
    if mtbf < seg.mtbf_min:
        # Sharp drop below minimum
        below = seg.mtbf_min - mtbf
        return max(0.0, 70.0 - below / 100.0)
    if mtbf >= seg.mtbf_max:
        return 100.0
    # Linear within range: 70 at min, 100 at max
    return 70.0 + 30.0 * (mtbf - seg.mtbf_min) / (seg.mtbf_max - seg.mtbf_min)


def position_distance(product: Product, seg: Segment) -> float:
    """Euclidean distance from product position to segment's IDEAL SPOT."""
    dx = product.pfmn - seg.ideal_pfmn
    dy = product.size - seg.ideal_size
    return sqrt(dx * dx + dy * dy)


def position_score(product: Product, seg: Segment) -> float:
    """
    Score 0-100 based on distance from segment's ideal spot.
    Within FINE_CUT_RADIUS → linear 100 (at ideal) to 0 (at radius).
    Outside fine-cut → 0.
    """
    d = position_distance(product, seg)
    if d >= FINE_CUT_RADIUS:
        return 0.0
    return 100.0 * (1.0 - d / FINE_CUT_RADIUS)


def in_rough_cut(product: Product, seg: Segment) -> bool:
    """A product is 'in' a segment's rough-cut circle if within ROUGH_CUT_RADIUS of CENTER."""
    dx = product.pfmn - seg.center_pfmn
    dy = product.size - seg.center_size
    return sqrt(dx * dx + dy * dy) <= ROUGH_CUT_RADIUS


def weighted_score(product: Product, seg: Segment) -> float:
    """
    Weighted customer survey score (before Awareness/Accessibility multiplier).
    Result is 0-100.

    HARD CUTOFFS (return 0 entirely, product cannot compete in this segment):
      - Outside rough-cut circle (too far from segment center)
      - Price outside segment expected range (Capsim: customers won't buy)

    Otherwise: weighted sum of 4 criteria (Price + Age + MTBF + Position).
    """
    if not in_rough_cut(product, seg):
        return 0.0
    # Capsim hard rule: price out of range = product excluded from segment
    if product.price < seg.price_min or product.price > seg.price_max:
        return 0.0
    ps = price_score(product.price, seg) * seg.price_weight
    as_ = age_score(product.age, seg) * seg.age_weight
    ms = mtbf_score(product.mtbf, seg) * seg.mtbf_weight
    posS = position_score(product, seg) * seg.position_weight
    return ps + as_ + ms + posS


def net_score(product: Product, seg: Segment) -> float:
    """
    Final customer survey score: Weighted × Awareness × Accessibility.
    Both Awareness and Accessibility are 0..1.

    Per Capsim guide: Net = Base × (1 - (1-A)/2) × (1 - (1-Acc)/2)
                         = Base × (1+A)/2 × (1+Acc)/2
    This means even at A=0/Acc=0, product gets ~25% of base score.
    """
    base = weighted_score(product, seg)
    if base <= 0:
        return 0.0
    a = max(0.0, min(1.0, product.awareness))
    acc = max(0.0, min(1.0, product.accessibility.get(seg.name, 0.0)))
    return base * (1 + a) / 2 * (1 + acc) / 2


def score_breakdown(product: Product, seg: Segment) -> dict:
    """Detailed breakdown for debugging/UI display."""
    base = weighted_score(product, seg)
    return {
        "product": product.name,
        "segment": seg.name,
        "in_rough_cut": in_rough_cut(product, seg),
        "price_raw": price_score(product.price, seg),
        "price_weighted": price_score(product.price, seg) * seg.price_weight,
        "age_raw": age_score(product.age, seg),
        "age_weighted": age_score(product.age, seg) * seg.age_weight,
        "mtbf_raw": mtbf_score(product.mtbf, seg),
        "mtbf_weighted": mtbf_score(product.mtbf, seg) * seg.mtbf_weight,
        "position_raw": position_score(product, seg),
        "position_weighted": position_score(product, seg) * seg.position_weight,
        "position_distance": position_distance(product, seg),
        "weighted_total": base,
        "awareness": product.awareness,
        "accessibility": product.accessibility.get(seg.name, 0.0),
        "net_score": net_score(product, seg),
    }


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    andrews = state.get_company("Andrews")
    print("=== Andrews R0 Customer Survey Scores (per segment) ===\n")
    for p in andrews.products:
        primary_seg = state.get_segment(p.primary_segment)
        breakdown = score_breakdown(p, primary_seg)
        print(f"{p.name} ({p.primary_segment}):")
        print(f"  Price ${p.price:.2f}: raw {breakdown['price_raw']:.1f} -> weighted {breakdown['price_weighted']:.1f}")
        print(f"  Age {p.age:.1f}y vs ideal {primary_seg.ideal_age:.1f}: raw {breakdown['age_raw']:.1f} -> weighted {breakdown['age_weighted']:.1f}")
        print(f"  MTBF {p.mtbf}: raw {breakdown['mtbf_raw']:.1f} -> weighted {breakdown['mtbf_weighted']:.1f}")
        print(f"  Position ({p.pfmn},{p.size}) vs ideal ({primary_seg.ideal_pfmn:.1f},{primary_seg.ideal_size:.1f}) "
              f"dist {breakdown['position_distance']:.2f}: raw {breakdown['position_raw']:.1f} -> weighted {breakdown['position_weighted']:.1f}")
        print(f"  Weighted Total: {breakdown['weighted_total']:.1f}")
        print(f"  Awareness {breakdown['awareness']*100:.0f}%, Accessibility {breakdown['accessibility']*100:.0f}%")
        print(f"  NET SCORE: {breakdown['net_score']:.1f}\n")
