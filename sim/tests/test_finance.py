"""Tests for sim.engines.finance: ratios, bonds, stock price, credit rating."""
from __future__ import annotations

import pytest

from sim.data.r0_seed import build_r0_state
from sim.engines.finance import (
    compute_ratios,
    calculate_credit_rating,
    max_new_bond_capacity,
    issue_bond,
    retire_bond_early,
    update_stock_price,
    income_statement,
    short_term_rate,
    long_term_rate,
    emergency_loan_rate,
    total_bond_interest,
    BOND_BROKERAGE_FEE,
    EARLY_RETIRE_FEE,
    MAX_BOND_DEBT_RATIO,
    EMERGENCY_LOAN_PENALTY,
    TAX_RATE,
)


@pytest.fixture
def state():
    return build_r0_state()


class TestCreditRating:
    def test_rating_brackets(self):
        assert calculate_credit_rating(1.0) == "AAA"
        assert calculate_credit_rating(1.5) == "AA"
        assert calculate_credit_rating(2.0) == "A"
        assert calculate_credit_rating(2.5) == "BBB"
        assert calculate_credit_rating(3.0) == "BB"
        assert calculate_credit_rating(3.5) == "B"
        assert calculate_credit_rating(10.0) == "D"

    def test_higher_leverage_lower_rating(self):
        # Rating ordering
        order = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "C", "DDD", "DD", "D"]
        seen = []
        for lev in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0]:
            seen.append(calculate_credit_rating(lev))
        assert seen == order


class TestComputeRatios:
    def test_andrews_r0_ratios(self, state):
        andrews = state.get_company("Andrews")
        ratios = compute_ratios(andrews)
        # ROS 12.3%
        assert ratios["ROS"] == pytest.approx(0.123, abs=0.01)
        # ROE 28.3%
        assert ratios["ROE"] == pytest.approx(0.283, abs=0.01)
        # Asset turnover 1.32
        assert ratios["Asset_Turnover"] == pytest.approx(1.32, abs=0.02)
        # Leverage 1.74
        assert ratios["Leverage"] == pytest.approx(1.74, abs=0.02)


class TestBondCapacity:
    def test_max_bond_capacity_andrews_50M(self, state):
        """Plant $96.8M * 80% - current bonds $27.2M = ~$50.3M."""
        andrews = state.get_company("Andrews")
        cap = max_new_bond_capacity(andrews)
        # 96,824,000 * 0.80 - 27,209,000 = 77,459,200 - 27,209,000 = 50,250,200
        assert cap == pytest.approx(50_250_200, abs=10_000)

    def test_max_bond_uses_80_pct_ratio(self):
        assert MAX_BOND_DEBT_RATIO == 0.80


class TestBondIssueAndRetire:
    def test_issue_bond_charges_5pct_fee(self, state):
        andrews = state.get_company("Andrews")
        cash_before = andrews.cash
        n_bonds_before = len(andrews.bonds)
        result = issue_bond(andrews, 10_000_000, state.prime_interest_rate, 2026)
        # 5% fee
        assert result["fee"] == pytest.approx(10_000_000 * BOND_BROKERAGE_FEE)
        assert result["net_proceeds"] == pytest.approx(10_000_000 * 0.95)
        # New bond added
        assert len(andrews.bonds) == n_bonds_before + 1
        # Cash up by net proceeds
        assert andrews.cash == pytest.approx(cash_before + result["net_proceeds"])

    def test_issue_bond_capped_at_capacity(self, state):
        andrews = state.get_company("Andrews")
        cap = max_new_bond_capacity(andrews)
        # Request way more than cap
        result = issue_bond(andrews, cap * 2, state.prime_interest_rate, 2026)
        assert result["issued"] <= cap + 1  # allow tiny rounding

    def test_retire_bond_early_fee(self, state):
        andrews = state.get_company("Andrews")
        bond = andrews.bonds[0]
        face = bond.face_value
        cash_before = andrews.cash
        result = retire_bond_early(andrews, bond.series)
        # Fee is 1.5% of face
        assert result["fee"] == pytest.approx(face * EARLY_RETIRE_FEE)
        # Bond removed
        assert bond not in andrews.bonds
        # Cash decreased
        assert andrews.cash < cash_before


class TestStockPrice:
    def test_update_stock_price_returns_positive(self, state):
        andrews = state.get_company("Andrews")
        price = update_stock_price(andrews)
        assert price > 0
        # Market cap recalculated
        assert andrews.market_cap == pytest.approx(price * andrews.shares_outstanding)


class TestInterestRates:
    def test_short_term_rate_above_prime(self):
        assert short_term_rate(0.08) == pytest.approx(0.085)

    def test_long_term_rate_depends_on_rating(self):
        # AAA gets smallest spread
        aaa = long_term_rate(0.08, "AAA")
        ccc = long_term_rate(0.08, "CCC")
        assert aaa < ccc

    def test_emergency_loan_has_7_5_penalty(self):
        prime = 0.08
        st = short_term_rate(prime)
        em = emergency_loan_rate(prime)
        assert em - st == pytest.approx(EMERGENCY_LOAN_PENALTY)


class TestIncomeStatement:
    def test_total_bond_interest_positive(self, state):
        andrews = state.get_company("Andrews")
        interest = total_bond_interest(andrews)
        # Sum coupons * face
        expected = sum(b.face_value * b.coupon_rate for b in andrews.bonds)
        assert interest == pytest.approx(expected)

    def test_income_statement_returns_keys(self, state):
        andrews = state.get_company("Andrews")
        is_dict = income_statement(andrews, 2026, state.prime_interest_rate)
        for key in ["sales", "variable_total", "contribution_margin", "ebit",
                    "pretax_income", "taxes", "net_profit"]:
            assert key in is_dict

    def test_income_statement_taxes_35pct(self, state):
        # Set up a clean company with known sales
        andrews = state.get_company("Andrews")
        # Make sure we can compute taxes; if pretax positive, taxes = 35%
        is_dict = income_statement(andrews, 2026, state.prime_interest_rate)
        if is_dict["pretax_income"] > 0:
            assert is_dict["taxes"] == pytest.approx(is_dict["pretax_income"] * TAX_RATE, rel=0.01)
