"""
Demand allocation + Segment drift engine.

Per Capsim:
  1. Each segment's center drifts by (drift_pfmn, drift_size) per year
     (segments move toward smaller + faster every year)
  2. Total segment demand grows by `growth_rate` per year
  3. Industry demand is allocated to products by:
        your_share = your_net_score / sum(all_net_scores_in_segment)
  4. Products score in MULTIPLE segments (if within rough-cut circle of each)
     but primary segment gets the strongest match
  5. Stockouts: if a product runs out, demand spills to next-best alternative

Reference: https://ww3.capsim.com/guides/professor/professor-guide/11-sensor-customer-buying-criteria77ba.cfm
"""
from __future__ import annotations
from typing import Dict, List, Tuple
from sim.data_models import GameState, Product, Segment, Company
from sim.engines.customer_score import net_score, in_rough_cut


def drift_segments(state: GameState) -> None:
    """Advance segment centers by one year of drift. Updates state in place."""
    for seg in state.segments:
        seg.center_pfmn += seg.drift_pfmn
        seg.center_size += seg.drift_size


def grow_industry_demand(state: GameState) -> Dict[str, int]:
    """
    Compute next year's total industry demand per segment using growth rate.
    Returns dict {segment_name: units}.
    """
    new_demand = {}
    for seg in state.segments:
        last_demand = state.industry_unit_demand.get(seg.name, 0)
        new_demand[seg.name] = int(round(last_demand * (1 + seg.growth_rate)))
    return new_demand


def all_products(state: GameState) -> List[Product]:
    """Flat list of all products across all companies."""
    out = []
    for c in state.companies:
        out.extend(c.products)
    return out


def compute_segment_scores(state: GameState, seg: Segment) -> List[Tuple[Product, float]]:
    """
    For one segment, compute every product's net score (sorted descending).
    Only products in rough-cut circle and with score > 0 are included.

    Applies TQM demand_increase per company (e.g., QFD Effort boosts demand).
    """
    # Build company TQM lookup
    tqm_boost = {c.name: 1.0 + c.tqm.demand_increase for c in state.companies}
    scored = []
    for p in all_products(state):
        s = net_score(p, seg) * tqm_boost.get(p.company, 1.0)
        if s > 0:
            scored.append((p, s))
    scored.sort(key=lambda x: -x[1])
    return scored


def allocate_demand(state: GameState, industry_demand: Dict[str, int]) -> Dict[str, Dict[str, int]]:
    """
    Allocate industry demand among products per segment using customer survey scores.

    Returns:
        {segment_name: {product_name: units_demanded}}

    Note: This is "potential" demand, before stockout adjustments.
    """
    result: Dict[str, Dict[str, int]] = {}
    for seg in state.segments:
        seg_total = industry_demand.get(seg.name, 0)
        scored = compute_segment_scores(state, seg)
        score_sum = sum(s for _, s in scored)
        seg_alloc: Dict[str, int] = {}
        if score_sum <= 0 or seg_total <= 0:
            result[seg.name] = seg_alloc
            continue
        for p, s in scored:
            share = s / score_sum
            seg_alloc[p.name] = int(round(seg_total * share))
        result[seg.name] = seg_alloc
    return result


def apply_stockouts(
    state: GameState,
    demand_by_segment: Dict[str, Dict[str, int]],
) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Simulate stockout reallocation.

    For each product, total demanded = sum of demands across segments.
    If product has limited inventory + production, only ship that much.
    Excess demand is reassigned to the next-best product in same segment.

    Returns:
        units_sold: {product_name: units_actually_sold}
        units_demanded_total: {product_name: total_demand_summed_across_segments}
    """
    # Step 1: Compute total demand per product across all segments
    total_demand: Dict[str, int] = {}
    for seg_name, alloc in demand_by_segment.items():
        for pname, units in alloc.items():
            total_demand[pname] = total_demand.get(pname, 0) + units

    # Step 2: Compute available supply per product = inventory + production
    available: Dict[str, int] = {}
    for p in all_products(state):
        available[p.name] = p.inventory + p.production_schedule

    # Step 3: Allocate sales per segment (in order of demand), spill stockouts
    units_sold: Dict[str, int] = {p.name: 0 for p in all_products(state)}
    remaining_supply = available.copy()

    for seg in state.segments:
        scored = compute_segment_scores(state, seg)  # ordered by score desc
        seg_demand = demand_by_segment.get(seg.name, {})
        # First pass: fulfill demand in score order
        unmet_in_segment = 0
        for p, _ in scored:
            want = seg_demand.get(p.name, 0)
            have = remaining_supply.get(p.name, 0)
            ship = min(want, have)
            units_sold[p.name] += ship
            remaining_supply[p.name] -= ship
            if want > ship:
                unmet_in_segment += want - ship
        # Second pass: redistribute unmet demand to next-best products
        if unmet_in_segment > 0:
            for p, _ in scored:
                if unmet_in_segment <= 0:
                    break
                have = remaining_supply.get(p.name, 0)
                if have > 0:
                    extra = min(unmet_in_segment, have)
                    units_sold[p.name] += extra
                    remaining_supply[p.name] -= extra
                    unmet_in_segment -= extra

    return units_sold, total_demand


def compute_actual_industry_sales(units_sold: Dict[str, int], state: GameState) -> Dict[str, int]:
    """Compute actual units sold per segment (sums where products sold)."""
    # Simplification: attribute units to product's primary segment
    # (in reality, units split by segment of buyer — we approximate)
    out: Dict[str, int] = {s.name: 0 for s in state.segments}
    for p in all_products(state):
        out[p.primary_segment] = out.get(p.primary_segment, 0) + units_sold.get(p.name, 0)
    return out


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    # Simulate "R1 prep": drift segments, grow demand
    print("=== R0 -> R1 drift demo ===\n")
    print("Segments BEFORE drift:")
    for s in state.segments:
        print(f"  {s.name}: center ({s.center_pfmn},{s.center_size}) ideal ({s.ideal_pfmn:.1f},{s.ideal_size:.1f})")

    next_demand = grow_industry_demand(state)
    drift_segments(state)
    state.industry_unit_demand = next_demand
    state.round_num = 1
    state.year = 2026

    print("\nSegments AFTER drift (R1):")
    for s in state.segments:
        print(f"  {s.name}: center ({s.center_pfmn},{s.center_size}) ideal ({s.ideal_pfmn:.1f},{s.ideal_size:.1f})")

    print(f"\nR1 Industry demand: {next_demand} (total {sum(next_demand.values())})")

    # Schedule some production for Andrews
    for p in state.get_company("Andrews").products:
        p.production_schedule = p.capacity_first_shift  # 1-shift output
    for c in state.companies:
        if c.name != "Andrews":
            for p in c.products:
                p.production_schedule = p.capacity_first_shift

    alloc = allocate_demand(state, next_demand)
    print("\nDemand allocation by segment (top 3 per segment):")
    for seg_name, items in alloc.items():
        sorted_items = sorted(items.items(), key=lambda x: -x[1])[:5]
        print(f"  {seg_name}: " + ", ".join(f"{n}={u}" for n, u in sorted_items))

    units_sold, total_demand = apply_stockouts(state, alloc)
    print("\nUnits sold (after stockout reallocation):")
    for p in all_products(state):
        print(f"  {p.name} ({p.company}/{p.primary_segment}): demand {total_demand.get(p.name,0)} -> sold {units_sold[p.name]} (inv+prod {p.inventory + p.production_schedule})")
