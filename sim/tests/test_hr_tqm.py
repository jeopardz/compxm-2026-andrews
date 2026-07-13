"""Tests for HR and TQM engines."""
from __future__ import annotations

import pytest

from sim.data.r0_seed import build_r0_state
from sim.engines.hr import (
    productivity_index,
    turnover_rate,
    employees_needed,
    update_hr,
    recruiting_cost,
    training_cost,
    BASE_TURNOVER,
    MAX_RECRUIT_SPEND,
    MAX_TRAINING_HOURS,
)
from sim.engines.tqm import (
    s_curve_factor,
    update_tqm,
    recommended_initiatives_for_round,
    TQM_IMPACTS,
    TQM_FULL_EFFECT_CUMULATIVE,
    TQM_PER_ROUND_CAP,
    INITIATIVE_NAMES,
)


@pytest.fixture
def state():
    return build_r0_state()


# ---------------- HR ----------------
class TestHRProductivity:
    def test_baseline_pi_is_1(self):
        assert productivity_index(0, 0) == pytest.approx(1.0)

    def test_max_pi_is_about_1_18(self):
        # Each factor contributes up to 9% -> 1 + 0.18 = 1.18
        assert productivity_index(MAX_RECRUIT_SPEND, MAX_TRAINING_HOURS) == pytest.approx(1.18, abs=0.005)

    def test_pi_monotonic_with_training(self):
        low = productivity_index(0, 0)
        mid = productivity_index(2500, 40)
        high = productivity_index(5000, 80)
        assert low < mid < high


class TestHRTurnover:
    def test_baseline_turnover_10pct(self):
        assert turnover_rate(0) == pytest.approx(BASE_TURNOVER)

    def test_max_training_turnover_5pct(self):
        # Max training cuts turnover to 5%
        assert turnover_rate(MAX_TRAINING_HOURS) == pytest.approx(0.05)

    def test_recruiting_cost_includes_auto_1k(self):
        # 10 hires, $0 extra spend -> 10 * 1000 = 10,000
        assert recruiting_cost(10, 0) == 10_000
        # 10 hires, $5000 extra -> 10 * 6000 = 60,000
        assert recruiting_cost(10, 5000) == 60_000

    def test_training_cost_per_hour_20(self):
        # 100 employees x 80 hours x $20 = $160,000
        assert training_cost(100, 80) == 160_000


class TestHRUpdate:
    def test_update_hr_sets_pi(self, state):
        apex = state.get_company("Apex")
        for p in apex.products:
            p.production_schedule = p.capacity_first_shift
        result = update_hr(apex, 5000, 80)
        assert result["productivity_index"] == pytest.approx(1.18, abs=0.005)
        assert result["turnover_rate"] == pytest.approx(0.05, abs=0.005)
        assert apex.hr.productivity_index == pytest.approx(1.18, abs=0.005)


# ---------------- TQM ----------------
class TestSCurve:
    def test_zero_spend_zero_factor(self):
        assert s_curve_factor(0) == 0.0

    def test_cap_spend_factor_one(self):
        assert s_curve_factor(TQM_FULL_EFFECT_CUMULATIVE) == 1.0
        assert s_curve_factor(10_000_000) == 1.0

    def test_monotonic_increasing(self):
        values = [s_curve_factor(x) for x in [0, 500_000, 1_000_000, 2_000_000, 3_000_000, 4_000_000]]
        assert values == sorted(values)


class TestTQMUpdate:
    def test_ten_initiatives_defined(self):
        assert len(INITIATIVE_NAMES) == 10
        assert len(TQM_IMPACTS) == 10

    def test_per_round_cap_enforced(self, state):
        apex = state.get_company("Apex")
        # Try to spend $5M on one initiative (over $2M cap)
        update_tqm(apex, {"QFD Effort": 5_000_000})
        # Cumulative should be capped at $2M for this round
        assert apex.tqm.cumulative_spend["QFD Effort"] == TQM_PER_ROUND_CAP

    def test_unknown_initiative_ignored(self, state):
        apex = state.get_company("Apex")
        result = update_tqm(apex, {"FakeInitiative": 1_000_000})
        assert result["round_spend"] == 0
        assert "FakeInitiative" not in apex.tqm.cumulative_spend

    def test_cumulative_accumulates(self, state):
        apex = state.get_company("Apex")
        update_tqm(apex, {"QFD Effort": 1_500_000})
        update_tqm(apex, {"QFD Effort": 1_500_000})
        # Two rounds at $1.5M each -> $3M cumulative
        assert apex.tqm.cumulative_spend["QFD Effort"] == pytest.approx(3_000_000)

    def test_recommended_initiatives_for_rounds(self):
        # R1 should recommend 6 initiatives totaling $9M
        r1 = recommended_initiatives_for_round(1)
        assert len(r1) == 6
        assert sum(r1.values()) == pytest.approx(9_000_000)
        # R4 -> just QFD
        r4 = recommended_initiatives_for_round(4)
        assert "QFD Effort" in r4
        # Unknown round -> empty
        assert recommended_initiatives_for_round(99) == {}

    def test_qfd_increases_demand(self, state):
        apex = state.get_company("Apex")
        # Spend $2M on QFD over 2 rounds -> $4M cumulative -> full effect
        update_tqm(apex, {"QFD Effort": 2_000_000})
        update_tqm(apex, {"QFD Effort": 2_000_000})
        # QFD (authentic mapping) = +0.045 demand + R&D cycle-time cut
        assert apex.tqm.demand_increase > 0
        assert apex.tqm.demand_increase == pytest.approx(0.045, abs=0.005)
        # QFD also shortens R&D cycle time now (its authentic second effect)
        assert apex.tqm.rd_cycle_time_reduction < 0
