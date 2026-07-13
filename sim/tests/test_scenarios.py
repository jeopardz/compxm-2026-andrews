"""Tests for the scenario generator + validation gauntlet.

Guarantees the SaaS "new puzzle every game" feature: scenarios are deterministic
(Reset reproduces them), balance-sheet consistent, and every scenario that the
validator accepts is playable to completion across all 4 rounds.
"""
from __future__ import annotations

from copy import deepcopy

import pytest

from sim.data.r0_seed import build_r0_state
from sim.data.scenarios import (
    DIFFICULTIES, build_scenario, generate_scenario, parse_scenario_id,
    seed_to_scenario_id,
)
from sim.data.scenario_validator import (
    PLAYER_COMPANY, baseline_player_decisions, validate_scenario,
)
from sim.engines.round_engine import advance_round


def _balance_error(company) -> float:
    net_plant = company.plant_value - company.accumulated_depreciation
    assets = (company.cash + company.accounts_receivable
              + company.inventory_value + net_plant)
    liab = (company.accounts_payable + company.current_debt
            + sum(b.face_value for b in company.bonds))
    equity = company.common_stock + company.retained_earnings
    return abs(assets - (liab + equity))


class TestIdParsing:
    def test_base_ids(self):
        for base in ("exam-a", "base", ""):
            assert parse_scenario_id(base) == (None, None)

    def test_seed_only(self):
        assert parse_scenario_id("gen-42") == (42, None)

    def test_seed_and_difficulty(self):
        assert parse_scenario_id("gen-42-hard") == (42, "hard")

    def test_unknown_difficulty_ignored(self):
        assert parse_scenario_id("gen-42-bogus") == (42, None)

    def test_freeform_id_hashes_stably(self):
        seed_a, _ = parse_scenario_id("my-custom-id")
        seed_b, _ = parse_scenario_id("my-custom-id")
        assert seed_a == seed_b and seed_a is not None

    def test_round_trip(self):
        assert parse_scenario_id(seed_to_scenario_id(7, "easy")) == (7, "easy")
        assert parse_scenario_id(seed_to_scenario_id(7)) == (7, None)


class TestDeterminism:
    def test_same_seed_same_board(self):
        a = generate_scenario(123, "normal")
        b = generate_scenario(123, "normal")
        assert a.model_dump() == b.model_dump()

    def test_difficulty_changes_board(self):
        easy = generate_scenario(123, "easy")
        hard = generate_scenario(123, "hard")
        assert easy.model_dump() != hard.model_dump()

    def test_build_scenario_reproduces_via_id(self):
        first = build_scenario("gen-55-hard")
        second = build_scenario("gen-55-hard")
        assert first.model_dump() == second.model_dump()


class TestBaseScenario:
    def test_exam_a_is_untouched_seed(self):
        assert build_scenario("exam-a").model_dump() == build_r0_state().model_dump()

    def test_base_passes_validation(self):
        rep = validate_scenario(build_r0_state())
        assert rep.ok, rep.failures
        assert rep.difficulty in ("Easy", "Normal", "Hard")


class TestBalanceSheet:
    @pytest.mark.parametrize("difficulty", DIFFICULTIES)
    def test_generated_books_balance(self, difficulty):
        for seed in range(1, 11):
            state = generate_scenario(seed, difficulty)
            for c in state.companies:
                err = _balance_error(c)
                assert err < 50_000, f"seed {seed} {difficulty} {c.name}: off ${err:,.0f}"


class TestValidatorRejectsBroken:
    def test_reject_zero_capacity(self):
        state = generate_scenario(1, "normal")
        state.get_company("Apex").products[0].capacity_first_shift = 0
        rep = validate_scenario(state)
        assert not rep.ok
        assert any("capacity" in f for f in rep.failures)

    def test_reject_position_off_map(self):
        state = generate_scenario(1, "normal")
        p = state.get_company("Apex").products[0]
        p.pfmn, p.size = 0.1, 0.1  # nowhere near any segment
        rep = validate_scenario(state)
        assert not rep.ok
        assert any("rough-cut" in f for f in rep.failures)

    def test_reject_price_out_of_band(self):
        state = generate_scenario(1, "normal")
        state.get_company("Apex").products[0].price = 999.0
        rep = validate_scenario(state)
        assert not rep.ok

    def test_reject_broken_balance_sheet(self):
        state = generate_scenario(1, "normal")
        state.get_company("Apex").retained_earnings += 5_000_000  # unbalance by $5M
        rep = validate_scenario(state)
        assert not rep.ok
        assert any("balance sheet" in f for f in rep.failures)


class TestPlaythroughCompletes:
    def test_validated_scenario_plays_four_rounds(self):
        state = generate_scenario(3, "normal")
        rep = validate_scenario(state)
        assert rep.ok, rep.failures
        # Independently replay to confirm the accepted scenario really finishes 4R.
        sim = deepcopy(state)
        for expected_round in range(1, 5):
            decisions = baseline_player_decisions(sim, PLAYER_COMPANY)
            result = advance_round(sim, decisions)
            assert result["round_num"] == expected_round
        assert sim.round_num == 4
        assert sim.get_company(PLAYER_COMPANY).emergency_loan == 0

    def test_r5_guard_still_holds(self):
        state = generate_scenario(3, "normal")
        sim = deepcopy(state)
        for _ in range(4):
            advance_round(sim, baseline_player_decisions(sim, PLAYER_COMPANY))
        with pytest.raises(ValueError):
            advance_round(sim, baseline_player_decisions(sim, PLAYER_COMPANY))


class TestDifficultyOrdering:
    def test_easy_scores_at_least_as_high_as_hard(self):
        """On the same seed, the easy variant should not be harder than the hard
        variant — baseline final stock (easy) >= baseline final stock (hard)."""
        wins = 0
        for seed in range(1, 9):
            easy = validate_scenario(generate_scenario(seed, "easy"))
            hard = validate_scenario(generate_scenario(seed, "hard"))
            if easy.final_stock and hard.final_stock and easy.final_stock >= hard.final_stock:
                wins += 1
        assert wins >= 7  # allow one noisy seed


class TestPoolYield:
    @pytest.mark.parametrize("difficulty", DIFFICULTIES)
    def test_most_seeds_pass(self, difficulty):
        passed = sum(validate_scenario(generate_scenario(s, difficulty)).ok
                     for s in range(1, 13))
        assert passed >= 9, f"{difficulty}: only {passed}/12 passed"


class TestPrebuiltPool:
    """If the offline pool has been built, every entry must still rebuild
    deterministically and pass validation (guards against a stale pool)."""

    def test_pool_entries_are_valid(self):
        from sim.data.scenario_pool import load_pool, build_from_entry
        pool = load_pool()
        if not pool:
            pytest.skip("scenario_pool.json not built")
        for entry in pool[:6]:  # spot-check a handful (full pool is exercised offline)
            for key in ("id", "seed", "difficulty", "final_stock"):
                assert key in entry
            rep = validate_scenario(build_from_entry(entry))
            assert rep.ok, f"{entry['id']}: {rep.failures}"
            assert rep.difficulty == entry["difficulty"]

    def test_pool_selection_avoids_played(self):
        from sim.data.scenario_pool import load_pool, pick_unplayed
        pool = load_pool()
        if not pool:
            pytest.skip("scenario_pool.json not built")
        played = [e["id"] for e in pool[:-1]]
        pick = pick_unplayed(played)
        assert pick["id"] == pool[-1]["id"]
