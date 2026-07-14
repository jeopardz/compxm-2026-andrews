"""
Customer Survey Score engine.

CompMastery scoring model (whole-score multiplier form):

  base (0-100)  = Σ criterion_fit × criterion_weight        # in-band appeal only
  net           = base
                × position_multiplier   # rough-cut: 1.0 in fine cut → 0 at rough edge
                × price_multiplier       # 1.0 in band; −20%/$1 above ceiling; 0 at +$5
                × mtbf_multiplier        # 1.0 ≥ min; −20%/1000hrs below; 0 at −5000
                × (1 + Awareness) / 2
                × (1 + Accessibility) / 2
                × (1 − AR_reduction)     # credit-terms penalty (see ar_reduction)

Why the multiplier form matters (vs. baking penalties into sub-scores): a price $3
over the ceiling in a segment where price is only 9% weighted should gut the WHOLE
score (~−60%), not just shave 9% off it. The old model baked penalties into each
sub-score, so out-of-band products stayed far too competitive.

For each segment, customers weight 4 criteria: Price, Age, MTBF (reliability),
Position (distance from the segment ideal spot).

Reference: CompMastery customer-survey scoring specification §4.4-4.6.
"""
from __future__ import annotations
from math import sqrt
from typing import Optional
from sim.data_models import Product, Segment


# Fine-cut circle radius: inside it, positioning gets full whole-score credit.
FINE_CUT_RADIUS = 2.5
# Rough-cut circle radius: beyond it, the product can't compete in the segment at all.
ROUGH_CUT_RADIUS = 4.0

# Accounts-receivable (credit terms) whole-score reduction, by days of lag.
# 90 days = 0 penalty (baseline generous terms) … 0 days (COD) = −40%.
AR_REDUCTION_BY_DAYS = {90: 0.0, 60: 0.007, 30: 0.07, 0: 0.40}


# ------------------------------------------------------------------
# In-band fit scores (0..100) — feed the weighted BASE. These carry NO
# rough-cut / out-of-band penalties; those are applied as whole-score
# multipliers below.
# ------------------------------------------------------------------

def price_score(price: float, seg: Segment) -> float:
    """In-band price appeal 0..100. Customers prefer the LOW end of the range.

      - At or below the floor -> 100 (best appeal; you sacrifice margin, not demand).
      - Within range: linear 100 (at min) down to 10 (at max).
      - At or above the ceiling: clamped at 10 here — the OVER-ceiling demand penalty
        is applied as a whole-score multiplier by price_multiplier(), not baked in.
    """
    range_size = seg.price_max - seg.price_min
    if range_size <= 0:
        return 50.0
    if price <= seg.price_min:
        return 100.0
    if price >= seg.price_max:
        return 10.0
    normalized = (price - seg.price_min) / range_size  # 0 at min, 1 at max
    return 100.0 * (1.0 - normalized * 0.9)            # 100 → 10 across the range


def age_score(age: float, seg: Segment) -> float:
    """Score 0-100 based on age vs segment's ideal age. Symmetric around ideal_age."""
    deviation = abs(age - seg.ideal_age)
    half_width = max(seg.ideal_age + 1.5, 2.0)  # at least 2yr tolerance
    if deviation >= half_width:
        return 0.0
    return 100.0 * (1.0 - deviation / half_width)


def mtbf_score(mtbf: float, seg: Segment) -> float:
    """In-band reliability appeal 0..100.

      - At or below the range min -> 70 (lowest in-band appeal). The BELOW-min demand
        penalty is applied by mtbf_multiplier(), not baked in here.
      - Within range: linear 70 (at min) up to 100 (at max).
      - At or above the range max: plateau at 100 (customers ignore extra reliability).
    """
    if mtbf <= seg.mtbf_min:
        return 70.0
    if mtbf >= seg.mtbf_max:
        return 100.0
    return 70.0 + 30.0 * (mtbf - seg.mtbf_min) / (seg.mtbf_max - seg.mtbf_min)


def position_distance(product: Product, seg: Segment) -> float:
    """Euclidean distance from product position to segment's IDEAL SPOT."""
    dx = product.pfmn - seg.ideal_pfmn
    dy = product.size - seg.ideal_size
    return sqrt(dx * dx + dy * dy)


def position_score(product: Product, seg: Segment) -> float:
    """In-fine-cut positioning appeal 0..100: 100 at the ideal spot, tapering to 40 at
    the fine-cut edge. Beyond the fine cut the in-band contribution is floored at 40 —
    the rough-cut demand penalty is applied separately by position_multiplier()."""
    d = position_distance(product, seg)
    if d <= FINE_CUT_RADIUS:
        return 100.0 - 60.0 * (d / FINE_CUT_RADIUS)
    return 40.0


# ------------------------------------------------------------------
# Whole-score multipliers (0..1) — rough-cut / out-of-band penalties
# ------------------------------------------------------------------

def position_multiplier(product: Product, seg: Segment) -> float:
    """Rough-cut whole-score penalty: 1.0 inside the fine cut, linear 1→0 across the
    2.5–4.0 rough band, 0 beyond the rough cut (product effectively can't sell here)."""
    d = position_distance(product, seg)
    if d <= FINE_CUT_RADIUS:
        return 1.0
    if d >= ROUGH_CUT_RADIUS:
        return 0.0
    return 1.0 - (d - FINE_CUT_RADIUS) / (ROUGH_CUT_RADIUS - FINE_CUT_RADIUS)


def price_multiplier(price: float, seg: Segment) -> float:
    """Over-ceiling price penalty on the WHOLE score: 1.0 in range (and below floor —
    a low price is a margin hit, not a demand hit); −20% per $1 above the ceiling; 0 at
    $5+ over (rough cut)."""
    if price <= seg.price_max:
        return 1.0
    over = price - seg.price_max
    return max(0.0, 1.0 - 0.20 * over)


def mtbf_multiplier(mtbf: float, seg: Segment) -> float:
    """Below-range reliability penalty on the WHOLE score: 1.0 at/above the range min;
    −20% per 1000 hrs below; 0 at 5000 below (rough cut). Above max is fine (plateau)."""
    if mtbf >= seg.mtbf_min:
        return 1.0
    below_k = (seg.mtbf_min - mtbf) / 1000.0
    return max(0.0, 1.0 - 0.20 * below_k)


def ar_reduction(ar_days: Optional[int]) -> float:
    """Whole-score reduction fraction from accounts-receivable (credit) terms.
    Interpolates the documented table (90d→0, 60d→0.7%, 30d→7%, 0d→40%). None → 0."""
    if ar_days is None:
        return 0.0
    pts = sorted(AR_REDUCTION_BY_DAYS.items())  # by days ascending
    if ar_days <= pts[0][0]:
        return pts[0][1]
    if ar_days >= pts[-1][0]:
        return pts[-1][1]
    for (d0, r0), (d1, r1) in zip(pts, pts[1:]):
        if d0 <= ar_days <= d1:
            t = (ar_days - d0) / (d1 - d0)
            return r0 + (r1 - r0) * t
    return 0.0


# ------------------------------------------------------------------
# Composite scores
# ------------------------------------------------------------------

def in_rough_cut(product: Product, seg: Segment) -> bool:
    """A product is 'in' a segment's rough-cut circle if within ROUGH_CUT_RADIUS of its
    CENTER (the gate for competing in the segment at all)."""
    dx = product.pfmn - seg.center_pfmn
    dy = product.size - seg.center_size
    return sqrt(dx * dx + dy * dy) <= ROUGH_CUT_RADIUS


def weighted_score(product: Product, seg: Segment,
                   mtbf_override: Optional[float] = None) -> float:
    """In-band weighted BASE score 0..100 (no rough-cut / out-of-band penalties — those
    are whole-score multipliers in net_score). Returns 0 only when the product is
    outside the segment's rough-cut circle entirely.

    mtbf_override: use this reliability (e.g. effective/line-blended MTBF) instead of the
    product's own for the reliability fit.
    """
    if not in_rough_cut(product, seg):
        return 0.0
    mtbf = product.mtbf if mtbf_override is None else mtbf_override
    ps = price_score(product.price, seg) * seg.price_weight
    as_ = age_score(product.age, seg) * seg.age_weight
    ms = mtbf_score(mtbf, seg) * seg.mtbf_weight
    posS = position_score(product, seg) * seg.position_weight
    return ps + as_ + ms + posS


def net_score(product: Product, seg: Segment,
              effective_mtbf: Optional[float] = None,
              ar_days: Optional[int] = None) -> float:
    """Final customer survey score.

    net = base × position_mult × price_mult × mtbf_mult × (1+A)/2 × (1+Acc)/2 × (1−AR)

    effective_mtbf: line-blended reliability (0.8×own + 0.2×line-lowest) used for BOTH
      the reliability fit and the below-range penalty. Defaults to the product's own.
    ar_days: accounts-receivable terms for the whole-score AR reduction (None = no
      reduction, i.e. generous 90-day baseline).
    """
    mtbf = product.mtbf if effective_mtbf is None else effective_mtbf
    base = weighted_score(product, seg, mtbf_override=mtbf)
    if base <= 0:
        return 0.0

    mult = (position_multiplier(product, seg)
            * price_multiplier(product.price, seg)
            * mtbf_multiplier(mtbf, seg))
    if mult <= 0:
        return 0.0

    a = max(0.0, min(1.0, product.awareness))
    acc = max(0.0, min(1.0, product.accessibility.get(seg.name, 0.0)))
    ar_mult = 1.0 - ar_reduction(ar_days)
    return base * mult * (1 + a) / 2 * (1 + acc) / 2 * ar_mult


def score_breakdown(product: Product, seg: Segment,
                    effective_mtbf: Optional[float] = None,
                    ar_days: Optional[int] = None) -> dict:
    """Detailed breakdown for debugging/UI display."""
    mtbf = product.mtbf if effective_mtbf is None else effective_mtbf
    base = weighted_score(product, seg, mtbf_override=mtbf)
    return {
        "product": product.name,
        "segment": seg.name,
        "in_rough_cut": in_rough_cut(product, seg),
        "price_raw": price_score(product.price, seg),
        "price_weighted": price_score(product.price, seg) * seg.price_weight,
        "age_raw": age_score(product.age, seg),
        "age_weighted": age_score(product.age, seg) * seg.age_weight,
        "mtbf_raw": mtbf_score(mtbf, seg),
        "mtbf_weighted": mtbf_score(mtbf, seg) * seg.mtbf_weight,
        "position_raw": position_score(product, seg),
        "position_weighted": position_score(product, seg) * seg.position_weight,
        "position_distance": position_distance(product, seg),
        "weighted_total": base,
        "position_multiplier": position_multiplier(product, seg),
        "price_multiplier": price_multiplier(product.price, seg),
        "mtbf_multiplier": mtbf_multiplier(mtbf, seg),
        "awareness": product.awareness,
        "accessibility": product.accessibility.get(seg.name, 0.0),
        "ar_reduction": ar_reduction(ar_days),
        "net_score": net_score(product, seg, effective_mtbf=effective_mtbf, ar_days=ar_days),
    }


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    apex = state.get_company("Apex")
    print("=== Apex R0 Customer Survey Scores (per segment) ===\n")
    for p in apex.products:
        primary_seg = state.get_segment(p.primary_segment)
        breakdown = score_breakdown(p, primary_seg)
        print(f"{p.name} ({p.primary_segment}):")
        print(f"  Price ${p.price:.2f}: raw {breakdown['price_raw']:.1f} -> weighted {breakdown['price_weighted']:.1f}")
        print(f"  Age {p.age:.1f}y vs ideal {primary_seg.ideal_age:.1f}: raw {breakdown['age_raw']:.1f} -> weighted {breakdown['age_weighted']:.1f}")
        print(f"  MTBF {p.mtbf}: raw {breakdown['mtbf_raw']:.1f} -> weighted {breakdown['mtbf_weighted']:.1f}")
        print(f"  Position ({p.pfmn},{p.size}) vs ideal ({primary_seg.ideal_pfmn:.1f},{primary_seg.ideal_size:.1f}) "
              f"dist {breakdown['position_distance']:.2f}: raw {breakdown['position_raw']:.1f} -> weighted {breakdown['position_weighted']:.1f}")
        print(f"  Multipliers: pos {breakdown['position_multiplier']:.2f} x price {breakdown['price_multiplier']:.2f} x mtbf {breakdown['mtbf_multiplier']:.2f}")
        print(f"  Weighted Total: {breakdown['weighted_total']:.1f}")
        print(f"  Awareness {breakdown['awareness']*100:.0f}%, Accessibility {breakdown['accessibility']*100:.0f}%")
        print(f"  NET SCORE: {breakdown['net_score']:.1f}\n")
