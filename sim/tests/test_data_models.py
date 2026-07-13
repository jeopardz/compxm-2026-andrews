"""Tests for sim.data_models schemas and sim.data.r0_seed initial state."""
from __future__ import annotations

import pytest

from sim.data_models import (
    Segment,
    Product,
    Company,
    Bond,
    HRState,
    TQMState,
    GameState,
    BSCScore,
    BoardQueryQuestion,
)
from sim.data.r0_seed import build_r0_state, R0_INDUSTRY_DEMAND


@pytest.fixture
def r0_state() -> GameState:
    return build_r0_state()


class TestSchemas:
    def test_segment_ideal_pfmn_size_computed(self):
        seg = Segment(
            name="Nano",
            center_pfmn=8.9, center_size=9.4,
            drift_pfmn=0.8, drift_size=-1.1,
            ideal_offset_pfmn=0.8, ideal_offset_size=-1.1,
            price_min=28, price_max=40, price_weight=0.27,
            ideal_age=1.0, age_weight=0.20,
            mtbf_min=18000, mtbf_max=24000, mtbf_weight=0.18,
            position_weight=0.35, growth_rate=0.14,
        )
        assert seg.ideal_pfmn == pytest.approx(9.7, abs=0.01)
        assert seg.ideal_size == pytest.approx(8.3, abs=0.01)

    def test_bond_basic_fields(self):
        b = Bond(series="13.5S2027", face_value=11_300_000,
                 coupon_rate=0.135, year_due=2027)
        assert b.series == "13.5S2027"
        assert b.market_close == 100.0  # default

    def test_company_total_equity_assets_liabilities(self):
        c = Company(name="Apex", products=[],
                    cash=10, accounts_receivable=5,
                    inventory_value=20, plant_value=100,
                    accumulated_depreciation=40,
                    accounts_payable=8, current_debt=12,
                    common_stock=50, retained_earnings=25,
                    shares_outstanding=1000)
        # total_assets = cash + AR + inv + (plant - depr)
        assert c.total_assets == pytest.approx(10 + 5 + 20 + 60)
        # total_liabilities = AP + current_debt + bonds (no bonds)
        assert c.total_liabilities == pytest.approx(20)
        assert c.total_equity == pytest.approx(75)
        assert c.book_value_per_share == pytest.approx(75 / 1000)

    def test_hrstate_defaults(self):
        h = HRState()
        assert h.productivity_index == pytest.approx(1.0)
        assert h.turnover_rate == pytest.approx(0.10)

    def test_tqmstate_defaults_zero(self):
        t = TQMState()
        assert t.total_expenditures == 0.0
        assert t.material_cost_reduction == 0.0
        assert t.spend_this_round == {}


class TestR0Seed:
    def test_r0_round_year(self, r0_state):
        assert r0_state.round_num == 0
        assert r0_state.year == 2025
        assert r0_state.prime_interest_rate == pytest.approx(0.08)

    def test_r0_four_companies(self, r0_state):
        names = [c.name for c in r0_state.companies]
        assert names == ["Apex", "Borealis", "Crestline", "Dynamo"]

    def test_r0_segments_four(self, r0_state):
        names = sorted(s.name for s in r0_state.segments)
        assert names == ["Core", "Elite", "Nano", "Thrift"]

    def test_apex_r0_reference_values(self, r0_state):
        apex = r0_state.get_company("Apex")
        assert apex.stock_price == pytest.approx(95.38, abs=0.01)
        assert apex.sales_last == pytest.approx(163_291_000, abs=1000)
        assert apex.ros == pytest.approx(0.123, abs=0.001)
        assert apex.roe == pytest.approx(0.283, abs=0.001)
        assert len(apex.products) == 4

    def test_industry_demand_totals(self, r0_state):
        assert R0_INDUSTRY_DEMAND["Thrift"] == 5101
        assert R0_INDUSTRY_DEMAND["Core"] == 6676
        assert R0_INDUSTRY_DEMAND["Nano"] == 3648
        assert R0_INDUSTRY_DEMAND["Elite"] == 3476
        assert sum(R0_INDUSTRY_DEMAND.values()) == 18_901
        assert r0_state.industry_unit_demand == R0_INDUSTRY_DEMAND

    def test_segment_centers_and_drift(self, r0_state):
        thrift = r0_state.get_segment("Thrift")
        core = r0_state.get_segment("Core")
        nano = r0_state.get_segment("Nano")
        elite = r0_state.get_segment("Elite")

        assert (thrift.center_pfmn, thrift.center_size) == pytest.approx((5.7, 14.3))
        assert (core.center_pfmn, core.center_size) == pytest.approx((7.4, 12.6))
        assert (nano.center_pfmn, nano.center_size) == pytest.approx((8.9, 9.4))
        assert (elite.center_pfmn, elite.center_size) == pytest.approx((10.6, 11.1))

        # Drift vectors
        assert (thrift.drift_pfmn, thrift.drift_size) == pytest.approx((0.5, -0.5))
        assert (core.drift_pfmn, core.drift_size) == pytest.approx((0.8, -0.8))
        assert (nano.drift_pfmn, nano.drift_size) == pytest.approx((0.8, -1.1))
        assert (elite.drift_pfmn, elite.drift_size) == pytest.approx((1.1, -0.8))

        # Growth rates
        assert thrift.growth_rate == pytest.approx(0.11)
        assert core.growth_rate == pytest.approx(0.10)
        assert nano.growth_rate == pytest.approx(0.14)
        assert elite.growth_rate == pytest.approx(0.16)

    def test_apex_bonds_total(self, r0_state):
        apex = r0_state.get_company("Apex")
        total = sum(b.face_value for b in apex.bonds)
        # 11.3M + 8.837M + 7.072M = 27.209M (~$27.2M)
        assert total == pytest.approx(27_209_000, abs=1000)
        assert len(apex.bonds) == 3

    def test_get_segment_get_company_get_product(self, r0_state):
        assert r0_state.get_segment("Core").name == "Core"
        assert r0_state.get_company("Borealis").name == "Borealis"
        assert r0_state.get_product("Atlas").company == "Apex"
        with pytest.raises(KeyError):
            r0_state.get_company("Unknown")
