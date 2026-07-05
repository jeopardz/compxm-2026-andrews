"""Tests for sim.engines.rd: revise mechanics, age halving, project timing."""
from __future__ import annotations

import pytest

from sim.data.r0_seed import build_r0_state
from sim.engines.rd import (
    rd_distance,
    rd_project_days,
    rd_project_cost,
    rd_completion_date,
    apply_revise,
    end_of_year_apply_completed_projects,
    advance_age_one_year,
    BASE_PROJECT_DAYS,
    DAYS_PER_DISTANCE_UNIT,
    BASE_RD_COST,
)


@pytest.fixture
def state():
    return build_r0_state()


class TestDistanceAndDays:
    def test_distance_zero_when_same_position(self, state):
        p = state.get_company("Andrews").products[0]
        assert rd_distance(p, p.pfmn, p.size) == pytest.approx(0.0)

    def test_distance_pythagorean(self, state):
        p = state.get_company("Andrews").products[0]
        # Move +3 pfmn, +4 size -> distance 5
        d = rd_distance(p, p.pfmn + 3, p.size + 4)
        assert d == pytest.approx(5.0)

    def test_zero_distance_minimum_days(self, state):
        # Same-position revise = MTBF-only project = BASE_PROJECT_DAYS
        p = state.get_company("Andrews").products[0]
        days = rd_project_days(p, p.pfmn, p.size)
        assert days == BASE_PROJECT_DAYS  # 60

    def test_days_grow_with_distance(self, state):
        p = state.get_company("Andrews").products[0]
        d_close = rd_project_days(p, p.pfmn + 0.5, p.size)
        d_far = rd_project_days(p, p.pfmn + 2.0, p.size)
        assert d_far > d_close

    def test_tqm_cycle_reduction_shortens_days(self, state):
        p = state.get_company("Andrews").products[0]
        normal = rd_project_days(p, p.pfmn + 1, p.size, rd_cycle_reduction=0.0)
        fast = rd_project_days(p, p.pfmn + 1, p.size, rd_cycle_reduction=0.40)
        # 40% reduction
        assert fast == pytest.approx(int(round(normal * 0.6)), abs=1)


class TestCost:
    def test_min_cost_is_base(self, state):
        p = state.get_company("Andrews").products[0]
        # Same position + same MTBF -> $1M base
        cost = rd_project_cost(p, p.pfmn, p.size, p.mtbf)
        assert cost == pytest.approx(BASE_RD_COST)

    def test_cost_increases_with_distance_and_mtbf(self, state):
        p = state.get_company("Andrews").products[0]
        cost1 = rd_project_cost(p, p.pfmn, p.size, p.mtbf)
        cost2 = rd_project_cost(p, p.pfmn + 1, p.size + 1, p.mtbf + 2000)
        assert cost2 > cost1


class TestApplyReviseAndCompletion:
    def test_apply_revise_sets_targets(self, state):
        p = state.get_company("Andrews").products[0]
        apply_revise(p, 6.0, 14.0, 20000, "2026-01-01")
        assert p.rd_target_pfmn == 6.0
        assert p.rd_target_size == 14.0
        assert p.rd_target_mtbf == 20000
        assert p.rd_completion_date is not None

    def test_short_revise_completes_and_halves_age(self, state):
        """Attic age 5.1 -> small revise (same pos, MTBF change) takes 60 days -> finishes in 2026."""
        p = state.get_company("Andrews").products[0]
        old_age = p.age
        apply_revise(p, p.pfmn, p.size, 18000, "2026-01-01")
        completed = end_of_year_apply_completed_projects(p, "2026-12-31")
        assert completed is True
        # After revise: new age = old_age / 2 + months_since_completion / 12
        # Completion ~ Mar 2 2026; months from Mar to Dec ~10
        # New age = 2.55 + 10/12 ≈ 3.38
        assert p.age < old_age  # Must be younger
        assert p.age == pytest.approx(old_age / 2.0 + 10/12.0, abs=0.2)

    def test_long_revise_does_not_complete_in_year(self, state):
        """A big revise (>~2.1 units, i.e. >365 days at 175 days/unit) spills over."""
        p = state.get_company("Andrews").products[0]
        # 3-unit move -> 175*3 = 525 days -> does NOT complete by end of 2026
        apply_revise(p, p.pfmn + 3.0, p.size, 20000, "2026-01-01")
        completed = end_of_year_apply_completed_projects(p, "2026-12-31")
        assert completed is False
        # Targets remain pending
        assert p.rd_target_pfmn is not None

    def test_advance_age_one_year(self, state):
        p = state.get_company("Andrews").products[0]
        old = p.age
        advance_age_one_year(p)
        assert p.age == pytest.approx(old + 1.0)


class TestCompletionDate:
    def test_completion_date_after_start(self):
        cd = rd_completion_date("2026-01-01", 90)
        assert cd > "2026-01-01"
        assert cd.startswith("2026-04")  # ~April 1
