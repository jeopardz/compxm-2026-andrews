"""Regression tests for the July 2026 security and consistency audit."""
from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

import sim.auth as auth
from sim.billing import checkout_url
from sim.board_query_gen import generate_round_queries
from sim.data.r0_seed import build_r0_state
from sim.data.scenario_pool import load_pool
from sim.data.scenarios import build_scenario
from sim.data_models import FinanceDecision, ProductDecision, RoundDecision, TQMDecision
from sim.engines.bsc import compute_cumulative_bsc
from sim.engines.demand import allocate_demand, apply_stockouts


def test_supabase_client_is_isolated_per_streamlit_session(monkeypatch):
    made = []

    def create_client(url, key):
        client = object()
        made.append(client)
        return client

    monkeypatch.setitem(sys.modules, "supabase", SimpleNamespace(create_client=create_client))
    monkeypatch.setattr(auth, "_secret", lambda key, default=None: {
        "SUPABASE_URL": "https://example.invalid", "SUPABASE_ANON_KEY": "anon"
    }.get(key, default))
    fake_st = SimpleNamespace(session_state={})
    monkeypatch.setattr(auth, "st", fake_st)
    first = auth.get_supabase()
    assert auth.get_supabase() is first
    fake_st.session_state = {}  # a second browser session
    second = auth.get_supabase()
    assert second is not first
    assert len(made) == 2


def test_checkout_parameters_are_url_encoded(monkeypatch):
    monkeypatch.setattr(auth, "_secret", lambda key, default=None: "https://pay.test/buy?x=1")
    url = checkout_url("user id/+", "name+tag@example.com")
    assert "user+id%2F%2B" in url
    assert "name%2Btag%40example.com" in url


@pytest.mark.parametrize("decision", [
    lambda: FinanceDecision(accounts_receivable_lag=-1),
    lambda: FinanceDecision(current_debt_borrow=1_000_000_000_000),
    lambda: TQMDecision(initiatives={"QFD Effort": 2_000_001}),
    lambda: ProductDecision(product_name="Atlas", price=-1),
])
def test_forged_decisions_are_rejected(decision):
    with pytest.raises(ValidationError):
        decision()


def test_recap_scores_never_go_negative():
    state = build_r0_state()
    company = state.get_company("Apex")
    company.cumulative_profit = -100_000_000
    company.roe = -5
    recap = compute_cumulative_bsc([{"metrics": {}}], state)
    assert recap.financial >= 0
    assert recap.total >= 0


def test_generated_board_query_options_are_unique_across_pool():
    for entry in load_pool():
        state = build_scenario(entry["id"])
        for round_num in range(1, 5):
            for question in generate_round_queries(state, round_num):
                assert len(question.options) == len(set(question.options))


def test_sales_are_recorded_by_actual_buyer_segment():
    state = build_r0_state()
    for company in state.companies:
        for product in company.products:
            product.production_schedule = product.capacity_first_shift
    allocation = allocate_demand(state, state.industry_unit_demand)
    sold, _ = apply_stockouts(state, allocation)
    for product in [p for c in state.companies for p in c.products]:
        assert sum(product.segment_sales_last.values()) == sold[product.name]


def test_webhook_uses_atomic_rpc_and_product_allowlist():
    source = open("supabase/functions/ls-webhook/index.ts", encoding="utf-8").read()
    migration = open("supabase/migrations/0003_security_and_consistency.sql", encoding="utf-8").read()
    assert 'rpc("process_ls_order"' in source
    assert "LS_STORE_ID" in source and "LS_VARIANT_IDS" in source
    assert "create or replace function public.process_ls_order" in migration.lower()
    assert "pg_advisory_xact_lock" in migration


def test_round_number_cannot_advance_past_game_contract():
    with pytest.raises(ValidationError):
        RoundDecision(round_num=5, products=[])
