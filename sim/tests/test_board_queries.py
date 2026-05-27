"""Tests for sim.board_queries: 30 questions, grading."""
from __future__ import annotations

import pytest

from sim.board_queries import (
    BOARD_QUERIES,
    get_round_queries,
    grade_round,
)
from sim.data_models import BoardQueryQuestion


class TestQuestionInventory:
    def test_total_questions_is_30(self):
        assert len(BOARD_QUERIES) == 30

    def test_expected_per_round(self):
        # R1=5, R2=6, R3=6, R4=6, R5=7
        expected = {1: 5, 2: 6, 3: 6, 4: 6, 5: 7}
        for rnd, count in expected.items():
            assert len(get_round_queries(rnd)) == count, f"Round {rnd}"

    def test_all_questions_have_4_options(self):
        for q in BOARD_QUERIES:
            assert len(q.options) == 4, f"{q.id} has {len(q.options)} options"

    def test_all_questions_correct_index_valid(self):
        for q in BOARD_QUERIES:
            assert 0 <= q.correct_index < 4, f"{q.id} correct_index {q.correct_index}"

    def test_all_questions_have_explanation(self):
        for q in BOARD_QUERIES:
            assert q.explanation, f"{q.id} missing explanation"

    def test_all_questions_have_unique_ids(self):
        ids = [q.id for q in BOARD_QUERIES]
        assert len(ids) == len(set(ids))


class TestGradeRound:
    def test_all_correct_full_score(self):
        # Submit all correct answers for round 1
        r1 = get_round_queries(1)
        answers = {q.id: q.correct_index for q in r1}
        result = grade_round(1, answers)
        assert result["correct"] == result["total"] == 5
        assert result["percent"] == pytest.approx(1.0)

    def test_all_wrong_zero_score(self):
        r1 = get_round_queries(1)
        # Choose an index that is NOT correct
        answers = {q.id: (q.correct_index + 1) % 4 for q in r1}
        result = grade_round(1, answers)
        assert result["correct"] == 0
        assert result["percent"] == pytest.approx(0.0)

    def test_partial_correct(self):
        r2 = get_round_queries(2)
        # Half correct
        answers = {}
        for i, q in enumerate(r2):
            answers[q.id] = q.correct_index if i % 2 == 0 else (q.correct_index + 1) % 4
        result = grade_round(2, answers)
        assert 0 < result["correct"] < result["total"]

    def test_grade_returns_details(self):
        r1 = get_round_queries(1)
        answers = {q.id: q.correct_index for q in r1}
        result = grade_round(1, answers)
        assert len(result["details"]) == 5
        for d in result["details"]:
            assert "id" in d
            assert "question" in d
            assert "is_correct" in d
            assert "explanation" in d
            assert d["is_correct"] is True

    def test_missing_answer_marked_wrong(self):
        # No answers provided
        result = grade_round(1, {})
        assert result["correct"] == 0
        assert result["total"] == 5
