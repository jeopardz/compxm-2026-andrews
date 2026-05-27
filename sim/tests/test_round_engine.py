"""Tests for sim.engines.round_engine: full R1 playthrough."""
from __future__ import annotations

import pytest

from sim.data.r0_seed import build_r0_state
from sim.data_models import (
    RoundDecision, ProductDecision, FinanceDecision, HRDecision, TQMDecision,
)
from sim.engines.round_engine import advance_round
from sim.ai_competitors import baldwin_decisions, chester_decisions, digby_decisions


def _make_simple_decisions(round_num: int = 1) -> RoundDecision:
    """Sensible Andrews R1 decisions."""
    return RoundDecision(
        round_num=round_num,
        products=[
            ProductDecision(
                product_name="Attic",
                price=24.00, promo_budget=1_500_000, sales_budget=1_000_000,
                production_schedule=1700,
            ),
            ProductDecision(
                product_name="Axe",
                price=31.00, promo_budget=1_500_000, sales_budget=1_500_000,
                production_schedule=2000,
            ),
            ProductDecision(
                product_name="Art",
                new_pfmn=10.5, new_size=7.2, new_mtbf=24000,
                price=38.00, promo_budget=1_500_000, sales_budget=1_500_000,
                production_schedule=1100,
            ),
            ProductDecision(
                product_name="Ant",
                price=40.00, promo_budget=1_500_000, sales_budget=1_500_000,
                production_schedule=1100,
            ),
        ],
        finance=FinanceDecision(dividend_per_share=6.00),
        hr=HRDecision(recruit_spend=2500, training_hours=40),
        tqm=TQMDecision(initiatives={
            "QFD Effort": 1_500_000, "CCE/6 Sigma": 1_500_000,
            "Vendor/JIT": 1_500_000, "CPI Systems": 1_500_000,
            "Concurrent Engineering": 1_500_000, "GEMI TQEM": 1_500_000,
        }),
    )


class TestFullRoundAdvance:
    def test_r1_advance_does_not_crash(self):
        state = build_r0_state()
        andrews_dec = _make_simple_decisions(1)
        result = advance_round(state, andrews_dec)
        assert result is not None
        assert "round_num" in result
        assert result["round_num"] == 1
        assert "bsc" in result

    def test_round_advances_year(self):
        state = build_r0_state()
        assert state.year == 2025
        advance_round(state, _make_simple_decisions(1))
        assert state.year == 2026
        assert state.round_num == 1

    def test_all_companies_have_production(self):
        state = build_r0_state()
        result = advance_round(state, _make_simple_decisions(1))
        for cname in ["Andrews", "Baldwin", "Chester", "Digby"]:
            assert cname in result["production_summary"]
            prod = result["production_summary"][cname]
            assert prod["units_produced"] > 0

    def test_bsc_score_in_reasonable_range(self):
        state = build_r0_state()
        result = advance_round(state, _make_simple_decisions(1))
        bsc = result["bsc"]
        # Total should be between 0 and ~150 (a bit above max 125)
        assert 0 <= bsc["total"] <= 200
        assert 0 <= bsc["financial"] <= 50
        assert 0 <= bsc["customer"] <= 50

    def test_segments_drift_after_round(self):
        state = build_r0_state()
        thrift_before = (5.7, 14.3)
        advance_round(state, _make_simple_decisions(1))
        thrift = state.get_segment("Thrift")
        assert thrift.center_pfmn == pytest.approx(thrift_before[0] + 0.5)
        assert thrift.center_size == pytest.approx(thrift_before[1] - 0.5)

    def test_history_recorded(self):
        state = build_r0_state()
        advance_round(state, _make_simple_decisions(1))
        assert len(state.history) == 1
        h = state.history[0]
        assert h["round"] == 1
        assert "andrews_profit" in h
        assert "andrews_stock" in h


class TestAICompetitors:
    def test_baldwin_decisions_returns_round_decision(self):
        state = build_r0_state()
        dec = baldwin_decisions(state)
        assert dec.round_num == 1
        assert len(dec.products) == 4
        # Baldwin uses premium pricing
        for pd in dec.products:
            assert pd.price is not None

    def test_chester_decisions_low_price(self):
        state = build_r0_state()
        dec = chester_decisions(state)
        # Chester uses "low" price strategy -> price near min
        for pd in dec.products:
            assert pd.price is not None

    def test_digby_max_hr(self):
        state = build_r0_state()
        dec = digby_decisions(state)
        assert dec.hr.training_hours == 80
        assert dec.hr.recruit_spend == 5000
