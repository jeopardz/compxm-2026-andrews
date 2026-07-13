"""
Personalized Board-Query generator.

BizSim's Board-Query mechanic gives every player the same topics, but
the numbers in each question are generated from THAT player's own simulation results,
and the correct answer is whatever their own company's data implies. This module
reproduces that — it reads a live GameState and emits `BoardQueryQuestion` objects
whose correct answer is computed directly from the engine (so it can never disagree
with what the game reports), plus plausible distractors built from the mistakes
students actually make (swapping ROA/ROE, forgetting xgrowth, using CM% for CM$, …).

The static bank in `board_queries.py` is kept as a study/fallback reference; the app
prefers these generated sets so the exam reflects the player's real board.

Deterministic: option order is a stable function of the question id (no RNG), so a
given state always yields the same graded answer — required for testing and for a fair
re-render of the same round.
"""
from __future__ import annotations

from typing import Dict, List, Callable

from sim.data_models import BoardQueryQuestion, GameState, Company, Segment
from sim.engines.finance import compute_ratios


RIVALS = ("Borealis", "Crestline", "Dynamo")


# ------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------

def _stable_index(qid: str, n: int) -> int:
    """Deterministic option slot for the correct answer (no RNG)."""
    return sum(ord(ch) for ch in qid) % n


def _mcq(qid: str, round_num: int, topic: str, question: str,
         correct: float, distractors: List[float],
         fmt: Callable[[float], str], explanation: str) -> BoardQueryQuestion:
    """Build a numeric multiple-choice question with the correct value placed at a
    deterministic slot and the distractors filling the rest, all formatted via `fmt`."""
    # Rounding can collapse different numeric distractors to the same visible
    # label. Nudge only colliding distractors until every displayed choice is
    # unambiguous; the computed correct value is never changed.
    unique_distractors: List[float] = []
    visible = {fmt(correct)}
    for original in distractors:
        candidate = original
        step = max(abs(original), abs(correct), 1.0) * 0.07
        attempt = 0
        while fmt(candidate) in visible:
            attempt += 1
            candidate = original + step * attempt
        visible.add(fmt(candidate))
        unique_distractors.append(candidate)
    distractors = unique_distractors
    n = len(distractors) + 1
    idx = _stable_index(qid, n)
    ordered: List[float] = [None] * n  # type: ignore
    ordered[idx] = correct
    di = iter(distractors)
    for i in range(n):
        if ordered[i] is None:
            ordered[i] = next(di)
    return BoardQueryQuestion(
        id=qid, round_num=round_num, topic=topic, question=question,
        options=[fmt(v) for v in ordered], correct_index=idx, explanation=explanation,
    )


def _pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def _ratio(v: float) -> str:
    return f"{v:.2f}"


def _money_m(v: float) -> str:
    return f"${v / 1e6:.1f}M"


def _units(v: float) -> str:
    return f"{int(round(v)):,}"


def _choice(qid: str, round_num: int, topic: str, question: str,
            correct_label: str, other_labels: List[str], explanation: str) -> BoardQueryQuestion:
    """Categorical MCQ (e.g. 'which company…'). Correct label placed deterministically."""
    n = len(other_labels) + 1
    idx = _stable_index(qid, n)
    ordered: List[str] = [None] * n  # type: ignore
    ordered[idx] = correct_label
    oi = iter(other_labels)
    for i in range(n):
        if ordered[i] is None:
            ordered[i] = next(oi)
    return BoardQueryQuestion(
        id=qid, round_num=round_num, topic=topic, question=question,
        options=ordered, correct_index=idx, explanation=explanation,
    )


# ------------------------------------------------------------------
# per-company financial questions
# ------------------------------------------------------------------

def _finance_questions(state: GameState, round_num: int, player: str) -> List[BoardQueryQuestion]:
    qs: List[BoardQueryQuestion] = []
    # Rotate which rival is asked about by round so the exam varies round to round.
    rival = RIVALS[(round_num - 1) % len(RIVALS)]

    for who in (player, rival):
        c = state.get_company(who)
        r = compute_ratios(c)
        tag = f"{who[:2].upper()}{round_num}"

        # ROS
        ros = r["ROS"]
        qs.append(_mcq(
            f"G{tag}ros", round_num, "Return on Sales",
            f"From {who}'s latest income statement (Net Profit {_money_m(c.profit_last)} on "
            f"Sales {_money_m(c.sales_last)}), what is {who}'s Return on Sales (ROS)?",
            ros, [ros + 0.05, ros - 0.04, r["ROA"]], _pct,
            f"ROS = Net Profit / Sales = {_money_m(c.profit_last)} / {_money_m(c.sales_last)} "
            f"= {_pct(ros)}. (A common trap is to use Total Assets instead of Sales — that's ROA.)",
        ))
        # Asset turnover
        at = r["Asset_Turnover"]
        qs.append(_mcq(
            f"G{tag}at", round_num, "Asset Turnover",
            f"{who} reports Sales {_money_m(c.sales_last)} and Total Assets "
            f"{_money_m(c.total_assets)}. What is its Asset Turnover?",
            at, [at * 1.3, at * 0.7, 1.0 / max(0.1, at)], _ratio,
            f"Asset Turnover = Sales / Total Assets = {at:.2f}.",
        ))
        # Leverage
        lev = r["Leverage"]
        qs.append(_mcq(
            f"G{tag}lev", round_num, "Leverage",
            f"{who} has Total Assets {_money_m(c.total_assets)} and Equity "
            f"{_money_m(c.total_equity)}. What is its Leverage (Assets/Equity)?",
            lev, [lev + 0.4, lev - 0.3, c.total_liabilities / max(1, c.total_equity)], _ratio,
            f"Leverage = Total Assets / Total Equity = {lev:.2f} (NOT Debt/Equity).",
        ))

    # DuPont / ROE for the player
    c = state.get_company(player)
    r = compute_ratios(c)
    roe = r["ROE"]
    qs.append(_mcq(
        f"G{player[:2].upper()}{round_num}roe", round_num, "Return on Equity",
        f"Using the DuPont identity (ROS x Asset Turnover x Leverage), what is {player}'s ROE?",
        roe, [roe + 0.06, roe - 0.05, r["ROA"]], _pct,
        f"ROE = ROS {_pct(r['ROS'])} x AT {r['Asset_Turnover']:.2f} x Leverage "
        f"{r['Leverage']:.2f} = {_pct(roe)} (= Net Profit / Equity).",
    ))
    return qs


def _contribution_margin_question(state: GameState, round_num: int, player: str) -> BoardQueryQuestion:
    c = state.get_company(player)
    cm_pct = c.contribution_margin_last / max(1.0, c.sales_last)
    return _mcq(
        f"M{player[:2].upper()}{round_num}cm", round_num, "Contribution Margin",
        f"{player}'s income statement shows Sales {_money_m(c.sales_last)} and Contribution "
        f"Margin {_money_m(c.contribution_margin_last)}. What is its Contribution Margin %?",
        cm_pct, [cm_pct + 0.08, cm_pct - 0.06, 1 - cm_pct], _pct,
        f"CM% = Contribution Margin / Sales = {_pct(cm_pct)}. Target is ≥30% early, ≥35% late.",
    )


# ------------------------------------------------------------------
# marketing / forecasting
# ------------------------------------------------------------------

def _forecast_question(state: GameState, round_num: int, player: str) -> BoardQueryQuestion:
    # Pick the fastest-growing segment for a forecasting question.
    seg = max(state.segments, key=lambda s: s.growth_rate)
    this_year = state.industry_unit_demand.get(seg.name, 0)
    nxt = this_year * (1 + seg.growth_rate)
    return _mcq(
        f"MK{round_num}fc", round_num, "Demand Forecasting",
        f"The {seg.name} segment sold {_units(this_year)} thousand units this year and grows "
        f"{seg.growth_rate * 100:.0f}% annually. What is next year's {seg.name} industry demand?",
        nxt, [this_year, nxt * (1 + seg.growth_rate), this_year * (1 - seg.growth_rate)], _units,
        f"Next demand = current x (1 + growth) = {_units(this_year)} x "
        f"{1 + seg.growth_rate:.2f} = {_units(nxt)} thousand. (Forgetting the xgrowth is the "
        f"classic error.)",
    )


def _best_ros_question(state: GameState, round_num: int, player: str) -> BoardQueryQuestion:
    ranked = sorted(state.companies, key=lambda c: compute_ratios(c)["ROS"], reverse=True)
    best = ranked[0].name
    others = [c.name for c in ranked[1:]]
    return _choice(
        f"S{round_num}ros", round_num, "Competitive Analysis",
        "Based on the latest financial results, which company achieved the HIGHEST "
        "Return on Sales (ROS) this year?",
        best, others,
        f"{best} led on ROS = Net Profit / Sales — the most profit squeezed from each sales dollar.",
    )


def _stock_leader_question(state: GameState, round_num: int, player: str) -> BoardQueryQuestion:
    ranked = sorted(state.companies, key=lambda c: c.stock_price, reverse=True)
    best = ranked[0].name
    others = [c.name for c in ranked[1:]]
    return _choice(
        f"S{round_num}stk", round_num, "Shareholder Value",
        "Which company currently has the highest stock price?",
        best, others,
        f"{best} has the highest stock price (driven by book value + last two years' EPS and "
        f"dividend).",
    )


# ------------------------------------------------------------------
# public API
# ------------------------------------------------------------------

def generate_round_queries(state: GameState, round_num: int,
                           player: str = "Apex") -> List[BoardQueryQuestion]:
    """Generate a personalized board-query set for one round from the live state.

    Finance-heavy (44% finance weighting), plus marketing/forecasting
    and competitive-analysis items. Every numeric answer is computed from the engine.
    """
    qs: List[BoardQueryQuestion] = []
    qs.extend(_finance_questions(state, round_num, player))          # ~7 finance
    qs.append(_contribution_margin_question(state, round_num, player))
    qs.append(_forecast_question(state, round_num, player))
    qs.append(_best_ros_question(state, round_num, player))
    qs.append(_stock_leader_question(state, round_num, player))
    return qs


def grade_generated(questions: List[BoardQueryQuestion], answers: Dict[str, int]) -> Dict:
    """Grade answers against a generated question list (same shape as
    board_queries.grade_round, but works on any question list)."""
    details = []
    correct = 0
    for q in questions:
        selected = answers.get(q.id)
        is_correct = selected == q.correct_index
        if is_correct:
            correct += 1
        details.append({
            "id": q.id, "question": q.question, "selected": selected,
            "correct": q.correct_index, "is_correct": is_correct,
            "explanation": q.explanation, "topic": q.topic,
        })
    total = len(questions)
    return {
        "round": questions[0].round_num if questions else 0,
        "correct": correct, "total": total,
        "percent": (correct / total) if total else 0.0,
        "details": details,
    }


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    for rnd in (1, 2):
        qs = generate_round_queries(state, rnd)
        print(f"\n=== Round {rnd}: {len(qs)} personalized questions ===")
        for q in qs:
            print(f"[{q.topic}] {q.question}")
            for i, opt in enumerate(q.options):
                mark = " <-- correct" if i == q.correct_index else ""
                print(f"    {chr(65+i)}. {opt}{mark}")
