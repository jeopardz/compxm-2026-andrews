"""Tests for sim.engines.demand: drift, growth, allocation, stockouts."""
from __future__ import annotations

import pytest

from sim.data.r0_seed import build_r0_state
from sim.engines.demand import (
    drift_segments,
    grow_industry_demand,
    allocate_demand,
    apply_stockouts,
    all_products,
    compute_segment_scores,
)


@pytest.fixture
def state():
    return build_r0_state()


class TestDrift:
    def test_drift_advances_thrift_center(self, state):
        before = state.get_segment("Thrift")
        old_pfmn, old_size = before.center_pfmn, before.center_size
        drift_segments(state)
        after = state.get_segment("Thrift")
        # Thrift: +0.5 pfmn, -0.5 size
        assert after.center_pfmn == pytest.approx(old_pfmn + 0.5)
        assert after.center_size == pytest.approx(old_size - 0.5)

    def test_drift_advances_all_segments(self, state):
        old = {s.name: (s.center_pfmn, s.center_size) for s in state.segments}
        drift_segments(state)
        for s in state.segments:
            new_pfmn, new_size = s.center_pfmn, s.center_size
            assert new_pfmn == pytest.approx(old[s.name][0] + s.drift_pfmn)
            assert new_size == pytest.approx(old[s.name][1] + s.drift_size)

    def test_elite_drifts_most(self, state):
        # Elite drift is +1.1/-0.8 - the most aggressive
        elite_before = state.get_segment("Elite")
        old = elite_before.center_pfmn
        drift_segments(state)
        elite_after = state.get_segment("Elite")
        assert elite_after.center_pfmn - old == pytest.approx(1.1)


class TestGrowth:
    def test_grow_industry_demand_uses_growth_rates(self, state):
        new_demand = grow_industry_demand(state)
        # Thrift 5101 * 1.11 = 5662.11 -> 5662
        assert new_demand["Thrift"] == 5662
        # Core 6676 * 1.10 = 7343.6 -> 7344
        assert new_demand["Core"] == 7344
        # Nano 3648 * 1.14 = 4158.72 -> 4159
        assert new_demand["Nano"] == 4159
        # Elite 3476 * 1.16 = 4032.16 -> 4032
        assert new_demand["Elite"] == 4032

    def test_total_demand_grows(self, state):
        old = sum(state.industry_unit_demand.values())  # 18901
        new_demand = grow_industry_demand(state)
        new_total = sum(new_demand.values())
        assert new_total > old
        # average growth ~12%
        ratio = new_total / old
        assert 1.10 < ratio < 1.15


class TestAllocation:
    def test_allocate_returns_dict_per_segment(self, state):
        # All products produce at capacity
        for p in all_products(state):
            p.production_schedule = p.capacity_first_shift
        alloc = allocate_demand(state, state.industry_unit_demand)
        assert set(alloc.keys()) == {"Thrift", "Core", "Nano", "Elite"}
        for seg_name, products in alloc.items():
            assert isinstance(products, dict)

    def test_allocated_units_sum_close_to_total_demand(self, state):
        for p in all_products(state):
            p.production_schedule = p.capacity_first_shift
        alloc = allocate_demand(state, state.industry_unit_demand)
        for seg in state.segments:
            allocated = sum(alloc[seg.name].values())
            target = state.industry_unit_demand[seg.name]
            # Should be within ~1% due to integer rounding
            assert abs(allocated - target) / max(target, 1) < 0.02, \
                f"{seg.name}: allocated {allocated}, target {target}"

    def test_compute_segment_scores_sorted_desc(self, state):
        thrift = state.get_segment("Thrift")
        scored = compute_segment_scores(state, thrift)
        # Sorted by score descending
        scores = [s for _, s in scored]
        assert scores == sorted(scores, reverse=True)


class TestStockouts:
    def test_no_supply_no_sales(self, state):
        for p in all_products(state):
            p.production_schedule = 0
            p.inventory = 0
        alloc = allocate_demand(state, state.industry_unit_demand)
        sold, demanded = apply_stockouts(state, alloc)
        for v in sold.values():
            assert v == 0

    def test_units_sold_not_exceeding_supply(self, state):
        # Limit each product to 100 units supply
        for p in all_products(state):
            p.production_schedule = 100
            p.inventory = 0
        alloc = allocate_demand(state, state.industry_unit_demand)
        sold, _ = apply_stockouts(state, alloc)
        for pname, units in sold.items():
            assert units <= 100, f"{pname} sold {units}, exceeded supply 100"

    def test_full_supply_meets_demand_or_better(self, state):
        # Very high supply -> sales should equal total demand summed across products
        for p in all_products(state):
            p.production_schedule = 100_000
        alloc = allocate_demand(state, state.industry_unit_demand)
        sold, demanded = apply_stockouts(state, alloc)
        total_sold = sum(sold.values())
        # With abundant supply, total sold should be ~ total demand (18,901 + rounding)
        total_industry = sum(state.industry_unit_demand.values())
        # Within 5% (some rounding/segment overlap effects)
        assert abs(total_sold - total_industry) / total_industry < 0.05
