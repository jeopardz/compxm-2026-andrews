"""Tests for sim.engines.customer_score."""
from __future__ import annotations

import pytest

from sim.data.r0_seed import build_r0_state
from sim.data_models import GameState, Product
from sim.engines.customer_score import (
    price_score,
    age_score,
    mtbf_score,
    position_score,
    in_rough_cut,
    weighted_score,
    net_score,
    score_breakdown,
    FINE_CUT_RADIUS,
)


@pytest.fixture
def state() -> GameState:
    return build_r0_state()


class TestPriceScore:
    def test_price_at_min_is_max_score(self, state):
        thrift = state.get_segment("Thrift")
        # Score at min price is 100
        assert price_score(thrift.price_min, thrift) == pytest.approx(100.0, abs=0.01)

    def test_price_outside_range_zero(self, state):
        thrift = state.get_segment("Thrift")  # range 14-26
        assert price_score(13.99, thrift) == 0.0
        assert price_score(26.01, thrift) == 0.0

    def test_price_at_max_lowest(self, state):
        thrift = state.get_segment("Thrift")
        # Linear: at max returns 100*(1 - 1.0*0.9) = 10.0
        assert price_score(thrift.price_max, thrift) == pytest.approx(10.0, abs=0.01)


class TestMTBFScore:
    def test_mtbf_at_max_is_100(self, state):
        elite = state.get_segment("Elite")  # min 20000 max 26000
        assert mtbf_score(elite.mtbf_max, elite) == pytest.approx(100.0)
        # Above max plateaus at 100
        assert mtbf_score(30000, elite) == pytest.approx(100.0)

    def test_mtbf_at_min_is_70(self, state):
        elite = state.get_segment("Elite")
        assert mtbf_score(elite.mtbf_min, elite) == pytest.approx(70.0)

    def test_mtbf_below_min_decays(self, state):
        elite = state.get_segment("Elite")
        # 1000 below min -> 70 - 1000/100 = 60
        score = mtbf_score(elite.mtbf_min - 1000, elite)
        assert score == pytest.approx(60.0)


class TestAgeScore:
    def test_age_at_ideal_perfect(self, state):
        thrift = state.get_segment("Thrift")  # ideal 3
        assert age_score(thrift.ideal_age, thrift) == pytest.approx(100.0)

    def test_age_zero_for_far_deviation(self, state):
        elite = state.get_segment("Elite")  # ideal 0
        # half_width = max(0+1.5, 2.0) = 2.0; deviation > 2 -> 0
        assert age_score(5.0, elite) == 0.0


class TestPositionAndRoughCut:
    def test_position_at_ideal_is_max(self, state):
        thrift = state.get_segment("Thrift")
        # Make a synthetic product at the segment's ideal spot
        attic = state.get_company("Andrews").products[0]
        attic.pfmn = thrift.ideal_pfmn
        attic.size = thrift.ideal_size
        assert position_score(attic, thrift) == pytest.approx(100.0)

    def test_position_outside_fine_cut_zero(self, state):
        thrift = state.get_segment("Thrift")
        attic = state.get_company("Andrews").products[0]
        attic.pfmn = thrift.ideal_pfmn + FINE_CUT_RADIUS + 0.1
        attic.size = thrift.ideal_size
        assert position_score(attic, thrift) == 0.0

    def test_rough_cut_membership(self, state):
        attic = state.get_company("Andrews").products[0]
        # Attic primary segment is Thrift
        thrift = state.get_segment("Thrift")
        assert in_rough_cut(attic, thrift) is True
        # And NOT in Elite rough cut
        elite = state.get_segment("Elite")
        assert in_rough_cut(attic, elite) is False


class TestWeightedAndNetScore:
    def test_weighted_score_outside_rough_cut_zero(self, state):
        attic = state.get_company("Andrews").products[0]
        elite = state.get_segment("Elite")
        assert weighted_score(attic, elite) == 0.0

    def test_net_score_andrews_products_have_positive_primary(self, state):
        # Each Andrews product should have a positive net score in its primary segment
        for p in state.get_company("Andrews").products:
            seg = state.get_segment(p.primary_segment)
            score = net_score(p, seg)
            assert score > 0, f"{p.name} should score > 0 in {seg.name}"

    def test_net_score_at_least_quarter_of_base(self, state):
        """Per net_score formula: net = base * (1+aw)/2 * (1+acc)/2 — min 25% of base."""
        attic = state.get_company("Andrews").products[0]
        # Zero out awareness/accessibility
        attic.awareness = 0.0
        attic.accessibility = {}
        thrift = state.get_segment("Thrift")
        base = weighted_score(attic, thrift)
        net = net_score(attic, thrift)
        if base > 0:
            assert net == pytest.approx(base * 0.25, rel=0.01)

    def test_score_breakdown_returns_keys(self, state):
        attic = state.get_company("Andrews").products[0]
        thrift = state.get_segment("Thrift")
        bd = score_breakdown(attic, thrift)
        for key in ["product", "segment", "in_rough_cut", "price_raw", "age_raw",
                    "mtbf_raw", "position_raw", "weighted_total", "net_score"]:
            assert key in bd
