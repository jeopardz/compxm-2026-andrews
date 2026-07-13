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
    position_multiplier,
    price_multiplier,
    mtbf_multiplier,
    ar_reduction,
    in_rough_cut,
    weighted_score,
    net_score,
    score_breakdown,
    FINE_CUT_RADIUS,
    ROUGH_CUT_RADIUS,
)


@pytest.fixture
def state() -> GameState:
    return build_r0_state()


class TestPriceScore:
    def test_price_at_min_is_max_score(self, state):
        thrift = state.get_segment("Thrift")
        # Score at min price is 100
        assert price_score(thrift.price_min, thrift) == pytest.approx(100.0, abs=0.01)

    def test_price_below_floor_is_max(self, state):
        # BizSim: pricing AT or BELOW the floor = max price appeal (you lose margin,
        # not demand). Previously this wrongly returned 0 (Atlas-at-$13 bug).
        thrift = state.get_segment("Thrift")  # range 14-26
        assert price_score(13.99, thrift) == pytest.approx(100.0)
        assert price_score(10.0, thrift) == pytest.approx(100.0)

    def test_price_at_max_lowest(self, state):
        thrift = state.get_segment("Thrift")
        # Linear: at max returns 100*(1 - 1.0*0.9) = 10.0
        assert price_score(thrift.price_max, thrift) == pytest.approx(10.0, abs=0.01)

    def test_price_above_max_clamps_at_10(self, state):
        # Over-ceiling appeal is clamped at 10 in the in-band score; the DEMAND penalty
        # is applied by price_multiplier(), not baked into price_score.
        thrift = state.get_segment("Thrift")
        assert price_score(30.0, thrift) == pytest.approx(10.0)


class TestWholeScoreMultipliers:
    def test_price_multiplier_over_ceiling(self, state):
        thrift = state.get_segment("Thrift")  # ceiling 26
        assert price_multiplier(26.0, thrift) == pytest.approx(1.0)   # in band
        assert price_multiplier(20.0, thrift) == pytest.approx(1.0)   # below floor = no penalty
        assert price_multiplier(27.0, thrift) == pytest.approx(0.80)  # $1 over -> -20%
        assert price_multiplier(28.0, thrift) == pytest.approx(0.60)  # $2 over -> -40%
        assert price_multiplier(31.0, thrift) == pytest.approx(0.0)   # $5+ over -> 0

    def test_mtbf_multiplier_below_min(self, state):
        elite = state.get_segment("Elite")  # min 20000
        assert mtbf_multiplier(20000, elite) == pytest.approx(1.0)
        assert mtbf_multiplier(30000, elite) == pytest.approx(1.0)   # above max fine
        assert mtbf_multiplier(19000, elite) == pytest.approx(0.80)  # 1000 below -> -20%
        assert mtbf_multiplier(15000, elite) == pytest.approx(0.0)   # 5000 below -> 0

    def test_position_multiplier_rough_cut(self, state):
        thrift = state.get_segment("Thrift")
        atlas = state.get_company("Apex").products[0]
        atlas.size = thrift.ideal_size
        atlas.pfmn = thrift.ideal_pfmn          # at ideal -> full
        assert position_multiplier(atlas, thrift) == pytest.approx(1.0)
        atlas.pfmn = thrift.ideal_pfmn + FINE_CUT_RADIUS   # fine-cut edge -> still 1.0
        assert position_multiplier(atlas, thrift) == pytest.approx(1.0)
        atlas.pfmn = thrift.ideal_pfmn + (FINE_CUT_RADIUS + ROUGH_CUT_RADIUS) / 2  # mid rough band
        assert position_multiplier(atlas, thrift) == pytest.approx(0.5, abs=0.01)
        atlas.pfmn = thrift.ideal_pfmn + ROUGH_CUT_RADIUS + 0.1   # beyond rough -> 0
        assert position_multiplier(atlas, thrift) == pytest.approx(0.0)

    def test_ar_reduction_table(self):
        assert ar_reduction(90) == pytest.approx(0.0)
        assert ar_reduction(60) == pytest.approx(0.007)
        assert ar_reduction(30) == pytest.approx(0.07)
        assert ar_reduction(0) == pytest.approx(0.40)
        assert ar_reduction(None) == 0.0


class TestMTBFScore:
    def test_mtbf_at_max_is_100(self, state):
        elite = state.get_segment("Elite")  # min 20000 max 26000
        assert mtbf_score(elite.mtbf_max, elite) == pytest.approx(100.0)
        # Above max plateaus at 100
        assert mtbf_score(30000, elite) == pytest.approx(100.0)

    def test_mtbf_at_min_is_70(self, state):
        elite = state.get_segment("Elite")
        assert mtbf_score(elite.mtbf_min, elite) == pytest.approx(70.0)

    def test_mtbf_below_min_clamps_at_70(self, state):
        # In-band score clamps at 70 at/below min; the below-min DEMAND penalty is
        # applied by mtbf_multiplier(), not baked into mtbf_score.
        elite = state.get_segment("Elite")
        assert mtbf_score(elite.mtbf_min - 1000, elite) == pytest.approx(70.0)


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
        atlas = state.get_company("Apex").products[0]
        atlas.pfmn = thrift.ideal_pfmn
        atlas.size = thrift.ideal_size
        assert position_score(atlas, thrift) == pytest.approx(100.0)

    def test_position_score_in_band_floor(self, state):
        # In-band positioning appeal: 100 at ideal, 40 at the fine-cut edge, and floored
        # at 40 beyond it (the rough-cut demand penalty is position_multiplier's job).
        thrift = state.get_segment("Thrift")
        atlas = state.get_company("Apex").products[0]
        atlas.size = thrift.ideal_size
        atlas.pfmn = thrift.ideal_pfmn + FINE_CUT_RADIUS
        assert position_score(atlas, thrift) == pytest.approx(40.0, abs=0.01)
        atlas.pfmn = thrift.ideal_pfmn + ROUGH_CUT_RADIUS + 0.1
        assert position_score(atlas, thrift) == pytest.approx(40.0)  # floored (penalty via multiplier)

    def test_rough_cut_membership(self, state):
        atlas = state.get_company("Apex").products[0]
        # Atlas primary segment is Thrift
        thrift = state.get_segment("Thrift")
        assert in_rough_cut(atlas, thrift) is True
        # And NOT in Elite rough cut
        elite = state.get_segment("Elite")
        assert in_rough_cut(atlas, elite) is False


class TestWeightedAndNetScore:
    def test_weighted_score_outside_rough_cut_zero(self, state):
        atlas = state.get_company("Apex").products[0]
        elite = state.get_segment("Elite")
        assert weighted_score(atlas, elite) == 0.0

    def test_net_score_apex_products_have_positive_primary(self, state):
        # Each Apex product should have a positive net score in its primary segment
        for p in state.get_company("Apex").products:
            seg = state.get_segment(p.primary_segment)
            score = net_score(p, seg)
            assert score > 0, f"{p.name} should score > 0 in {seg.name}"

    def test_net_score_at_least_quarter_of_base(self, state):
        """Per net_score formula: net = base * (1+aw)/2 * (1+acc)/2 — min 25% of base."""
        atlas = state.get_company("Apex").products[0]
        # Zero out awareness/accessibility
        atlas.awareness = 0.0
        atlas.accessibility = {}
        thrift = state.get_segment("Thrift")
        base = weighted_score(atlas, thrift)
        net = net_score(atlas, thrift)
        if base > 0:
            assert net == pytest.approx(base * 0.25, rel=0.01)

    def test_score_breakdown_returns_keys(self, state):
        atlas = state.get_company("Apex").products[0]
        thrift = state.get_segment("Thrift")
        bd = score_breakdown(atlas, thrift)
        for key in ["product", "segment", "in_rough_cut", "price_raw", "age_raw",
                    "mtbf_raw", "position_raw", "weighted_total", "net_score"]:
            assert key in bd
