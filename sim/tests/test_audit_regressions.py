"""Regression coverage for the July 2026 five-auditor findings."""
from __future__ import annotations

import pytest

from sim.data.r0_seed import build_r0_state
from sim.data_models import FinanceDecision, ProductDecision, RoundDecision
from sim.engines.bsc import compute_cumulative_bsc
from sim.engines.finance import (
    EMERGENCY_LOAN_PENALTY,
    STOCK_ISSUE_FEE_PCT,
    compute_ratios,
    income_statement,
    issue_stock,
)
from sim.engines.round_engine import advance_round, apply_company_decisions
from sim.tests.test_round_engine import _make_simple_decisions


def _balance_error(company) -> float:
    return company.total_assets - company.total_liabilities - company.total_equity


def test_insolvent_company_cannot_receive_aaa_rating():
    company = build_r0_state().get_company("Apex")
    company.cash = -500_000_000
    ratios = compute_ratios(company)
    assert company.total_assets < 0
    assert ratios["S&P"] == "DDD"


def test_capped_stock_issue_deducts_percentage_fee_from_cash():
    company = build_r0_state().get_company("Apex")
    cash_before = company.cash
    max_shares = int(company.shares_outstanding * 0.20)
    result = issue_stock(company, 1_000_000_000)
    gross = max_shares * 95.38
    assert result["shares"] == max_shares
    assert result["fee"] == pytest.approx(gross * STOCK_ISSUE_FEE_PCT)
    assert company.cash - cash_before == pytest.approx(gross * (1 - STOCK_ISSUE_FEE_PCT))


def test_emergency_loan_penalty_is_charged_in_income_statement():
    company = build_r0_state().get_company("Apex")
    company.emergency_loan = 4_000_000
    before = income_statement(company, 2026, 0.08)
    assert before["emergency_penalty_interest"] == pytest.approx(
        4_000_000 * EMERGENCY_LOAN_PENALTY
    )


def test_mtbf_input_is_clamped_before_entering_live_state():
    state = build_r0_state()
    company = state.get_company("Apex")
    decision = RoundDecision(
        round_num=1,
        products=[ProductDecision(product_name="Atlas", new_mtbf=-1)],
    )
    apply_company_decisions(company, decision, state, state.companies)
    assert company.products[0].rd_target_mtbf == 10_000


def test_automation_downgrade_keeps_historical_gross_plant_positive():
    state = build_r0_state()
    company = state.get_company("Apex")
    gross_before = company.plant_value
    decision = RoundDecision(
        round_num=1,
        products=[ProductDecision(product_name="Atlas", new_automation=1.0)],
    )
    apply_company_decisions(company, decision, state, state.companies)
    assert company.plant_value > gross_before
    assert company.plant_value - company.accumulated_depreciation > 0


def test_transaction_heavy_round_keeps_balance_sheet_balanced():
    state = build_r0_state()
    decision = _make_simple_decisions(1)
    decision.finance = FinanceDecision(
        issue_bond=8_000_000,
        retire_bond_early=[state.get_company("Apex").bonds[0].series],
        issue_stock=8_000_000,
    )
    decision.products[0].capacity_change = -100
    decision.products[0].new_automation = 4.0
    advance_round(state, decision)
    for company in state.companies:
        assert abs(_balance_error(company)) < 50_000


def test_matured_bond_rolls_for_one_year_instead_of_immediate_repayment():
    state = build_r0_state()
    company = state.get_company("Apex")
    company.bonds[0].year_due = state.year + 1
    matured_face = company.bonds[0].face_value
    decision = _make_simple_decisions(1)
    decision.finance = FinanceDecision(current_debt_borrow=0)
    result = advance_round(state, decision)
    assert company.current_debt >= matured_face
    assert result["financials"]["Apex"]["long_term_interest"] >= matured_face * 0.01


def test_recap_productivity_component_is_capped_at_50_raw_points():
    state = build_r0_state()
    state.get_company("Apex").hr.productivity_index = 9.0
    history = [{"metrics": {}}]
    recap = compute_cumulative_bsc(history, state)
    assert recap.learning_growth <= 20.0
