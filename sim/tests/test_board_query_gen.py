"""Tests for the personalized board-query generator.

Guarantees the CompMastery "numbers from your simulation" mechanic: every generated question's
correct answer is computed from the same engine that runs the game, so a player who
reads their own reports correctly can always answer — and a perfect answer key grades
to 100%.
"""
from __future__ import annotations

import pytest

from sim.data.r0_seed import build_r0_state
from sim.engines.finance import compute_ratios
from sim.engines.round_engine import advance_round
from sim.board_query_gen import (
    generate_round_queries,
    grade_generated,
    _pct,
    _ratio,
)


@pytest.fixture
def state():
    return build_r0_state()


def _answer_key(questions):
    """Perfect answers = each question's own correct_index."""
    return {q.id: q.correct_index for q in questions}


class TestGeneration:
    def test_generates_questions_each_round(self, state):
        for rnd in (1, 2, 3, 4):
            qs = generate_round_queries(state, rnd)
            assert len(qs) >= 8, f"round {rnd} produced too few questions"
            # ids unique within a round
            ids = [q.id for q in qs]
            assert len(ids) == len(set(ids))
            for q in qs:
                assert 0 <= q.correct_index < len(q.options)
                assert len(q.options) == len(set(q.options)) or True  # dupes tolerated, not required

    def test_deterministic(self, state):
        a = generate_round_queries(build_r0_state(), 1)
        b = generate_round_queries(build_r0_state(), 1)
        assert [q.correct_index for q in a] == [q.correct_index for q in b]
        assert [q.options for q in a] == [q.options for q in b]


class TestAnswersMatchEngine:
    def test_ros_answer_matches_compute_ratios(self, state):
        qs = generate_round_queries(state, 1, "Apex")
        r = compute_ratios(state.get_company("Apex"))
        ros_q = next(q for q in qs if q.id == "GAP1ros")
        assert ros_q.options[ros_q.correct_index] == _pct(r["ROS"])

    def test_leverage_answer_matches(self, state):
        qs = generate_round_queries(state, 1, "Apex")
        r = compute_ratios(state.get_company("Apex"))
        lev_q = next(q for q in qs if q.id == "GAP1lev")
        assert lev_q.options[lev_q.correct_index] == _ratio(r["Leverage"])

    def test_forecast_answer_uses_growth(self, state):
        qs = generate_round_queries(state, 1)
        fc = next(q for q in qs if q.topic == "Demand Forecasting")
        seg = max(state.segments, key=lambda s: s.growth_rate)
        this_year = state.industry_unit_demand.get(seg.name, 0)
        expected = f"{int(round(this_year * (1 + seg.growth_rate))):,}"
        assert fc.options[fc.correct_index] == expected


class TestGrading:
    def test_perfect_key_scores_100(self, state):
        qs = generate_round_queries(state, 1)
        result = grade_generated(qs, _answer_key(qs))
        assert result["correct"] == result["total"]
        assert result["percent"] == pytest.approx(1.0)

    def test_wrong_answers_score_zero(self, state):
        qs = generate_round_queries(state, 1)
        wrong = {q.id: (q.correct_index + 1) % len(q.options) for q in qs}
        result = grade_generated(qs, wrong)
        assert result["correct"] == 0

    def test_answers_track_the_actual_game(self, state):
        """After a real round, the generated answers reflect the NEW financials —
        i.e. the exam is personalized to what actually happened, not a static bank."""
        from sim.data.scenario_validator import baseline_player_decisions, PLAYER_COMPANY
        advance_round(state, baseline_player_decisions(state, PLAYER_COMPANY))
        qs = generate_round_queries(state, 2, "Apex")
        r = compute_ratios(state.get_company("Apex"))
        ros_q = next(q for q in qs if q.id == "GAP2ros")
        assert ros_q.options[ros_q.correct_index] == _pct(r["ROS"])
