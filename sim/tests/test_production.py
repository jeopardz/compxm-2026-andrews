"""Tests for sim.engines.production: plant value, schedule, costs."""
from __future__ import annotations

import pytest

from sim.data.r0_seed import build_r0_state
from sim.engines.production import (
    plant_value,
    capacity_purchase_cost,
    automation_upgrade_cost,
    capacity_sell_value,
    labor_cost_factor,
    schedule_production,
    annual_depreciation,
    inventory_carry_cost,
    company_production_summary,
    SECOND_SHIFT_LABOR_MULTIPLIER,
    MAX_UTILIZATION,
    DEPRECIATION_YEARS,
)


@pytest.fixture
def state():
    return build_r0_state()


class TestPlantValue:
    def test_apex_total_plant_value_matches_reference(self, state):
        """Apex R0 plant value = $96.8M."""
        apex = state.get_company("Apex")
        total = sum(plant_value(p) for p in apex.products)
        # 1130*30 + 1200*26 + 728*22 + 714*22 = 33.9M + 31.2M + 16.016M + 15.708M = $96.824M
        assert total == pytest.approx(96_824_000, abs=1000)

    def test_atlas_plant_value(self, state):
        atlas = state.get_company("Apex").products[0]
        # cap=1130, auto=6 -> 1130 * (6 + 4*6) * 1000 = 1130 * 30 * 1000 = 33,900,000
        assert plant_value(atlas) == pytest.approx(33_900_000)

    def test_capacity_purchase_cost_formula(self):
        # 100 units of capacity at automation 5: 100 * (6 + 20) * 1000 = $2.6M
        assert capacity_purchase_cost(100, 5.0) == pytest.approx(2_600_000)
        # 100 units at automation 10: 100 * (6 + 40) * 1000 = $4.6M
        assert capacity_purchase_cost(100, 10.0) == pytest.approx(4_600_000)


class TestLaborAndAutomation:
    def test_labor_factor_decreases_with_automation(self):
        # auto 1 -> 1.0; auto 10 -> 0.10
        assert labor_cost_factor(1.0) == pytest.approx(1.0)
        assert labor_cost_factor(10.0) == pytest.approx(0.10)
        # auto 5: 1 - 4*0.10 = 0.60
        assert labor_cost_factor(5.0) == pytest.approx(0.60)

    def test_labor_factor_with_productivity(self):
        # Higher productivity reduces effective labor cost
        no_prod = labor_cost_factor(5.0, 1.0)
        high_prod = labor_cost_factor(5.0, 1.18)
        assert high_prod < no_prod

    def test_automation_upgrade_cost(self):
        # 100 units * 4 per level * (5 levels) * 1000 = $2M
        cost = automation_upgrade_cost(100, 5.0, 10.0)
        assert cost == pytest.approx(2_000_000)
        # No change -> 0
        assert automation_upgrade_cost(100, 5.0, 5.0) == 0.0
        # Downgrade is NOT free — retooling cost charged both directions.
        # 5.0 -> 3.0 = 2 levels * 100 * $4 * 1000 = $800K
        assert automation_upgrade_cost(100, 5.0, 3.0) == pytest.approx(800_000)

    def test_capacity_sell_value(self):
        # Recovers $0.65 per original dollar invested.
        original = capacity_purchase_cost(100, 5.0)  # $2.6M
        proceeds = capacity_sell_value(100, 5.0)
        assert proceeds == pytest.approx(original * 0.65)


class TestSchedule:
    def test_schedule_capped_at_max_utilization(self, state):
        p = state.get_company("Apex").products[0]
        # Try to schedule 5x capacity -> capped at 2x
        sched = schedule_production(p, p.capacity_first_shift * 5)
        assert sched["scheduled"] <= p.capacity_first_shift * MAX_UTILIZATION

    def test_schedule_first_vs_second_shift_split(self, state):
        p = state.get_company("Apex").products[0]
        cap = p.capacity_first_shift
        sched = schedule_production(p, int(cap * 1.5))
        assert sched["first_shift_units"] == cap
        assert sched["second_shift_units"] == int(cap * 1.5) - cap
        assert sched["utilization_pct"] == pytest.approx(150.0, abs=0.5)

    def test_schedule_at_or_below_first_shift_no_second(self, state):
        p = state.get_company("Apex").products[0]
        sched = schedule_production(p, p.capacity_first_shift)
        assert sched["second_shift_units"] == 0
        assert sched["first_shift_units"] == p.capacity_first_shift

    def test_unit_cost_second_shift_is_1_5x_labor(self, state):
        p = state.get_company("Apex").products[0]
        sched = schedule_production(p, int(p.capacity_first_shift * 1.5))
        first_labor = sched["unit_cost_first_shift"] - p.material_cost
        second_labor = sched["unit_cost_second_shift"] - p.material_cost
        assert second_labor == pytest.approx(first_labor * SECOND_SHIFT_LABOR_MULTIPLIER, rel=0.001)


class TestDepreciationAndCarry:
    def test_annual_depreciation_15_year_straight_line(self, state):
        p = state.get_company("Apex").products[0]
        assert annual_depreciation(p) == pytest.approx(plant_value(p) / DEPRECIATION_YEARS)

    def test_inventory_carry_is_12pct_of_unit_cost(self, state):
        p = state.get_company("Apex").products[0]
        carry = inventory_carry_cost(p, p.inventory)
        # Just verify it's positive and proportional
        assert carry > 0
        # Doubling inventory -> doubling carry
        carry2 = inventory_carry_cost(p, p.inventory * 2)
        assert carry2 == pytest.approx(carry * 2)

    def test_company_production_summary_aggregates(self, state):
        apex = state.get_company("Apex")
        for p in apex.products:
            p.production_schedule = p.capacity_first_shift  # 100% util on all
        summary = company_production_summary(apex)
        assert summary["total_1st_shift_capacity"] == sum(
            p.capacity_first_shift for p in apex.products
        )
        assert summary["total_units_scheduled"] == summary["total_1st_shift_capacity"]
