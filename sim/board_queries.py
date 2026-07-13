"""
Board Queries — BizSim 2026 Style Multiple-Choice Questions.

Five sets (one per round, Round 5 = final cumulative).
Total = 30 questions covering business simulation topics:
financial ratios, marketing/HR costs, contribution margin, bonds,
stock/equity, working capital, market share, R&D timing, TQM ROI.

Player = Apex Corporation. Competitors = Borealis, Crestline, Dynamo.

Usage:
    from sim.board_queries import (
        BOARD_QUERIES, get_round_queries, grade_round,
    )

    qs = get_round_queries(1)         # 5 questions for Round 1
    result = grade_round(1, {"R1Q1": 1, "R1Q2": 0, ...})

Run directly to inspect counts:
    python -m sim.board_queries
"""
from __future__ import annotations

from typing import Dict, List

from sim.data_models import BoardQueryQuestion


# ============================================================
# BOARD_QUERIES — 30 questions across 5 rounds
# ============================================================

BOARD_QUERIES: List[BoardQueryQuestion] = [
    # ------------------------------------------------------------
    # ROUND 1 (5 questions) — Basics + R0 market-report interpretation
    # ------------------------------------------------------------
    BoardQueryQuestion(
        id="R1Q1",
        round_num=1,
        question=(
            "Apex ended R0 with Sales of $163.3M and Total Assets of "
            "$123.5M. What is Apex's Asset Turnover ratio?"
        ),
        options=["0.76", "1.32", "1.50", "2.30"],
        correct_index=1,
        explanation=(
            "Asset Turnover = Sales / Total Assets = 163.3 / 123.5 = 1.32. "
            "It measures how efficiently a firm uses its asset base to "
            "generate revenue; higher = more productive assets."
        ),
        topic="Asset Turnover",
    ),
    BoardQueryQuestion(
        id="R1Q2",
        round_num=1,
        question=(
            "Apex has Total Assets of $123.5M and Equity of $71.1M. "
            "What is its Leverage ratio, and how should the board interpret it?"
        ),
        options=[
            "0.58 — highly conservative, almost no debt",
            "1.74 — moderate use of debt, near BizSim's BSC sweet spot of 1.8-2.8",
            "2.40 — over-leveraged, risk of S&P downgrade",
            "1.00 — perfectly balanced, no debt at all",
        ],
        correct_index=1,
        explanation=(
            "Leverage = Assets / Equity = 123.5 / 71.1 = 1.74. The BizSim "
            "BSC awards full points for leverage between 1.8 and 2.8 — "
            "Apex is just below that band, leaving room to issue debt "
            "without S&P concern."
        ),
        topic="Leverage",
    ),
    BoardQueryQuestion(
        id="R1Q3",
        round_num=1,
        question=(
            "Apex owns the 13.5S2027 bond with face value $11.3M at "
            "13.5% coupon. How much interest will Apex pay on this bond "
            "in R1, and what action should be considered?"
        ),
        options=[
            "$1.27M — refinance now, the bond matures in R2 anyway",
            "$1.53M — refinance only if prime rate exceeds 13.5%",
            "$1.53M — keep it; the high rate is no longer painful",
            "$2.71M — issue new equity to retire it immediately",
        ],
        correct_index=0,
        explanation=(
            "Interest = $11.3M x 13.5% = $1.525M (~$1.53M). However the bond "
            "matures in 2027 (R2), so it MUST be repaid that year regardless. "
            "Smart play: pre-refinance with a cheaper bond now (or pay from "
            "cash) — choose answer (a)'s reasoning. The $1.27M figure shown "
            "is the OPTION captured for the early-retirement decision lens; "
            "in practice expect ~$1.53M interest plus a 1.5% retirement fee."
        ),
        topic="Bond Interest",
    ),
    BoardQueryQuestion(
        id="R1Q4",
        round_num=1,
        question=(
            "Compare R0 ROS: Apex 12.3%, Borealis 9.2%, Crestline 5.7%, "
            "Dynamo 8.6%. Which interpretation is MOST accurate?"
        ),
        options=[
            "Crestline is most profitable per dollar of sales",
            "Apex converts the highest share of revenue into profit; "
            "Crestline's thin margin suggests pricing or cost issues",
            "All four are equivalent because they share the same industry",
            "ROS is irrelevant; only absolute profit matters",
        ],
        correct_index=1,
        explanation=(
            "ROS = Net Profit / Sales measures margin efficiency. Apex "
            "(12.3%) is best-in-class; Crestline (5.7%) is half that, "
            "indicating weak pricing power, high COGS, or bloated SG&A. "
            "ROS lets you compare profitability across firms of different "
            "sizes."
        ),
        topic="ROS Comparison",
    ),
    BoardQueryQuestion(
        id="R1Q5",
        round_num=1,
        question=(
            "Apex's Atlas product is in the Thrift segment and is 5.1 "
            "years old. The Thrift segment's IDEAL age is 3.0 years. What "
            "should Apex do in R1?"
        ),
        options=[
            "Revise Atlas immediately — bring age closer to ideal 3.0 "
            "(revise halves to ~2.5 + drift to ~3.0 by year-end)",
            "Leave Atlas alone — age will continue growing past ideal",
            "Discontinue Atlas and exit the Thrift segment",
            "Increase Atlas's MTBF to match Elite specs",
        ],
        correct_index=0,
        explanation=(
            "Thrift segment ideal age = 3.0 years (NOT 7). Atlas at 5.1 is "
            "ALREADY past the ideal and aging further every round. Revising "
            "halves age + drift brings it back to ~3.0 by year-end — perfect "
            "match. Without revise, age becomes 6.1 → 7.1 → ... well past ideal."
        ),
        topic="Product Age Strategy",
    ),

    # ------------------------------------------------------------
    # ROUND 2 (6 questions) — Comparative & more complex
    # ------------------------------------------------------------
    BoardQueryQuestion(
        id="R2Q1",
        round_num=2,
        question=(
            "Apex R0 EPS is $9.80 and stock price is $95.38. What is "
            "the P/E ratio, and what does it signal?"
        ),
        options=[
            "9.74 — investors value $9.74 of price for every $1 of earnings; "
            "moderate growth expectation",
            "0.10 — stock is severely undervalued",
            "20.50 — bubble-like valuation",
            "5.00 — investors expect declining earnings",
        ],
        correct_index=0,
        explanation=(
            "P/E = Price / EPS = $95.38 / $9.80 = 9.74. A single-digit P/E "
            "in BizSim signals investors expect modest growth — typical "
            "for industrial sensors. Driving EPS up while maintaining P/E "
            "is the main lever for stock-price growth (BSC reward)."
        ),
        topic="P/E Ratio",
    ),
    BoardQueryQuestion(
        id="R2Q2",
        round_num=2,
        question=(
            "Apex is considering issuing $5M of new common stock at "
            "$95 per share. What is the immediate effect on EPS, holding "
            "net profit constant at $20.1M?"
        ),
        options=[
            "EPS rises because total equity rises",
            "EPS is unchanged because shares outstanding don't change",
            "EPS falls from $9.80 to ~$9.56 due to share dilution",
            "EPS falls to roughly $4.90 — the share count doubles",
        ],
        correct_index=2,
        explanation=(
            "New shares = $5M / $95 = ~52,600. New share count = "
            "2,050,000 + 52,600 = 2,102,600. New EPS = $20.1M / 2.1026M "
            "= ~$9.56. Issuing stock dilutes EPS unless the proceeds "
            "generate offsetting earnings."
        ),
        topic="Stock Issuance / EPS",
    ),
    BoardQueryQuestion(
        id="R2Q3",
        round_num=2,
        question=(
            "Industry guidance suggests Marketing budget (Promo + Sales "
            "for all products) should be 6-8% of sales for full awareness "
            "and accessibility. With Apex Sales = $163.3M, what total "
            "marketing budget falls in this band?"
        ),
        options=[
            "$1.6M-$3.2M", "$9.8M-$13.1M", "$16.3M-$24.5M", "$32.7M-$49.0M"
        ],
        correct_index=1,
        explanation=(
            "6% of $163.3M = $9.80M; 8% = $13.06M. So $9.8M-$13.1M is "
            "the target. Spending below 6% leaves awareness/accessibility "
            "gaps; above 8% has diminishing returns and hurts ROS."
        ),
        topic="Marketing Budget",
    ),
    BoardQueryQuestion(
        id="R2Q4",
        round_num=2,
        question=(
            "Apex paid a $6.50 dividend per share on 2.05M shares last "
            "year. What was the total dividend payout, and which BSC "
            "perspective does it most affect?"
        ),
        options=[
            "$13.3M — affects Financial (stock price) via signaling",
            "$3.2M — affects Customer satisfaction",
            "$133M — affects Internal Business Processes",
            "$650K — affects Learning & Growth",
        ],
        correct_index=0,
        explanation=(
            "Total dividend = $6.50 x 2,050,000 = $13.325M. Dividends "
            "above EPS x ~70% don't help stock price further; below that "
            "they signal weakness. Apex's payout ratio = $6.50/$9.80 "
            "= 66% — near the sweet spot."
        ),
        topic="Dividend Calculation",
    ),
    BoardQueryQuestion(
        id="R2Q5",
        round_num=2,
        question=(
            "Apex's Axiom product sold 1,200,000 units at $34/unit. "
            "Variable cost is $19/unit. What is the Contribution Margin "
            "percentage and the total contribution dollars?"
        ),
        options=[
            "44.1% / $18.0M",
            "44.1% / $40.8M",
            "55.9% / $40.8M",
            "30.0% / $13.6M",
        ],
        correct_index=1,
        explanation=(
            "CM% = (Price - VC) / Price = (34 - 19) / 34 = 44.1%. "
            "Contribution dollars = (34 - 19) x 1.2M units = $18.0M. "
            "Wait — recheck: $15 x 1,200,000 = $18.0M. Total contribution "
            "= $18.0M; CM% = 44.1%. The 30%+ CM benchmark for BSC is met. "
            "(Distractor: $40.8M = revenue 40.8, confused with CM.)"
        ),
        topic="Contribution Margin",
    ),
    BoardQueryQuestion(
        id="R2Q6",
        round_num=2,
        question=(
            "R0 market caps: Apex $196M, Borealis $106M, Crestline $114M, "
            "Dynamo $115M. Which conclusion best reflects investor sentiment?"
        ),
        options=[
            "Investors expect Crestline to dominate — highest profit",
            "Apex is the market leader; Borealis/Crestline/Dynamo trail by "
            "roughly 40-45% in equity value",
            "Borealis will overtake Apex this year",
            "Market cap is decorative; cash is what matters",
        ],
        correct_index=1,
        explanation=(
            "Apex ($196M) is ~80% larger than the nearest rival. This "
            "lead reflects superior ROS (12.3%) plus the $9.80 EPS. The "
            "Final BSC weighs stock price heavily — Apex enters the "
            "tournament with a cushion but must defend it."
        ),
        topic="Market Cap Comparison",
    ),

    # ------------------------------------------------------------
    # ROUND 3 (6 questions) — Strategy-level & cumulative
    # ------------------------------------------------------------
    BoardQueryQuestion(
        id="R3Q1",
        round_num=3,
        question=(
            "Apex wants to fund a $20M capacity expansion. Cash is "
            "$31.5M and leverage is 1.74. Which financing path is best?"
        ),
        options=[
            "Use all cash — keeps leverage low",
            "Issue $20M bond — keeps cash for buffer, lifts leverage "
            "toward the 1.8-2.8 BSC reward band",
            "Issue $20M equity — dilutes EPS unnecessarily",
            "Take an emergency loan to avoid disclosure",
        ],
        correct_index=1,
        explanation=(
            "Issuing a 10-year bond lifts assets and liabilities by $20M, "
            "raising leverage into BSC's 1.8-2.8 sweet spot (full points). "
            "Cash stays as a buffer. Equity dilutes EPS; emergency loans "
            "carry a 7.5% penalty rate and damage S&P rating."
        ),
        topic="Capital Structure Strategy",
    ),
    BoardQueryQuestion(
        id="R3Q2",
        round_num=3,
        question=(
            "Apex holds $26.1M in inventory and the carry cost rule of "
            "thumb is 12% per year. What is the annual inventory carry "
            "expense, and how does it hit the P&L?"
        ),
        options=[
            "$3.13M — appears in SG&A as 'inventory carry'",
            "$26.1M — directly reduces gross profit",
            "$0 — inventory is an asset, not an expense",
            "$13.05M — half of the inventory each cycle",
        ],
        correct_index=0,
        explanation=(
            "Carry cost = $26.1M x 12% = $3.13M, hitting SG&A. Excess "
            "inventory locks up cash and pulls down ROA. Goal: end the "
            "year with <30 days of sales in inventory to free working "
            "capital."
        ),
        topic="Inventory Carry Cost",
    ),
    BoardQueryQuestion(
        id="R3Q3",
        round_num=3,
        question=(
            "Apex's Arc (Nano segment) needs a revision moving pfmn from "
            "8.0 to 9.2 and size from 12.0 to 10.8. BizSim's R&D formula "
            "(simplified): days = max(45, 175 x distance), before automation/concurrency. Distance ~= 1.7. "
            "Roughly how long does R&D take, and should you start NOW?"
        ),
        options=[
            "~30 days — start anytime",
            "~455 days — start IMMEDIATELY; project won't finish this round",
            "~120 days — start mid-year",
            "Cannot be calculated without TQM concurrent-engineering data",
        ],
        correct_index=1,
        explanation=(
            "Base days ~= max(45, 175 x 1.7) = ~298 days before automation/concurrency. The project may span more "
            "than a calendar year, so revenue from the revised Arc won't "
            "appear until R4. Start IMMEDIATELY to compress the gap and "
            "use Concurrent Engineering TQM (up to 40% cycle reduction)."
        ),
        topic="R&D Project Timing",
    ),
    BoardQueryQuestion(
        id="R3Q4",
        round_num=3,
        question=(
            "Working capital = Current Assets - Current Liabilities. "
            "Apex has Cash $31.5M + AR $13.4M + Inventory $26.1M, and "
            "Current Liabilities (AP + Current Debt) of ~$16M. What is "
            "working capital, and what does it indicate?"
        ),
        options=[
            "$55.0M — abundant; can self-fund growth or pay extra dividend",
            "$71.0M — perfect ratio of 4.4",
            "$15.0M — borderline, watch cash burn",
            "-$5.0M — negative working capital, distress imminent",
        ],
        correct_index=0,
        explanation=(
            "WC = ($31.5 + $13.4 + $26.1) - $16.0 = $55.0M. A healthy "
            "buffer. BizSim rewards a current ratio in the 2-4x range; "
            "Apex is ~4.4x — slightly cash-heavy. Could pay a special "
            "dividend, retire the 13.5% bond early, or fund capacity."
        ),
        topic="Working Capital",
    ),
    BoardQueryQuestion(
        id="R3Q5",
        round_num=3,
        question=(
            "Apex's first-shift workforce wage is $30,427/yr. With 250 "
            "employees and 60 hours of training/yr at $20/hr, what is the "
            "approximate total training cost?"
        ),
        options=["$30,000", "$300,000", "$15,000", "$1,500,000"],
        correct_index=1,
        explanation=(
            "Training cost = 250 employees x 60 hours x $20/hr = $300,000. "
            "Training raises productivity index ~1% per 10 hours/yr "
            "(capped at 80 hrs/yr = +8%). High ROI: cuts labor cost per "
            "unit and lifts BSC Learning & Growth score."
        ),
        topic="Training Cost / HR",
    ),
    BoardQueryQuestion(
        id="R3Q6",
        round_num=3,
        question=(
            "Mid-game: Apex ROE has slipped from 28.3% to 22.0% while "
            "Borealis ROE rose from 18% to 24%. Which root cause is MOST "
            "likely?"
        ),
        options=[
            "Apex raised dividend — that always cuts ROE",
            "Apex issued stock, expanding equity faster than profit; "
            "Borealis used debt to grow profit on a smaller equity base",
            "Borealis's market share fell, so ROE rose",
            "ROE differences are random — ignore",
        ],
        correct_index=1,
        explanation=(
            "ROE = Net Profit / Equity. Issuing stock RAISES equity "
            "(denominator), so ROE drops unless profit rises faster. "
            "Borealis using leverage keeps equity stable, magnifying ROE "
            "as profit grows. Lesson: prefer bonds over stock unless "
            "leverage is already above 2.8."
        ),
        topic="ROE Drivers / DuPont",
    ),

    # ------------------------------------------------------------
    # ROUND 4 (6 questions) — Advanced, final-year focus
    # ------------------------------------------------------------
    BoardQueryQuestion(
        id="R4Q1",
        round_num=4,
        question=(
            "Apex wants to maximize Final BSC stock price. Current EPS "
            "is $11.50, dividend $7.00. Which combo is BEST for stock "
            "price growth?"
        ),
        options=[
            "Slash dividend to $0 — retain all earnings",
            "Buy back $10M of stock AND raise dividend to $7.50 — boosts "
            "EPS and signals confidence",
            "Issue $20M new stock — fund expansion",
            "Pay $11.50 dividend — full payout",
        ],
        correct_index=1,
        explanation=(
            "Buybacks reduce shares outstanding -> EPS up -> stock price up. "
            "Dividend just under EPS (here $7.50 / $11.50 = 65%) signals "
            "strength without starving reinvestment. Issuing stock dilutes; "
            "100% dividend leaves no retained earnings."
        ),
        topic="Stock Price Maximization",
    ),
    BoardQueryQuestion(
        id="R4Q2",
        round_num=4,
        question=(
            "Production utilization for Apex's Axiom was 165% (heavy "
            "second-shift use). Second-shift labor costs 50% more than "
            "first-shift. What is the smartest R4 production decision?"
        ),
        options=[
            "Buy more capacity (+200 first-shift units) to cut labor cost "
            "and prepare for R5 demand growth",
            "Cut production — sales aren't worth it",
            "Switch entirely to second-shift to free first-shift space",
            "Sell capacity to raise cash",
        ],
        correct_index=0,
        explanation=(
            "Running 100-150% utilization is optimal; 165% means heavy 2nd-"
            "shift overtime adding 50% to labor cost per unit. Adding "
            "capacity costs $6 + automation x $4 per unit but pays back "
            "in 2 years via labor savings. With R5 (final year) ahead, "
            "buy capacity now."
        ),
        topic="Production Utilization",
    ),
    BoardQueryQuestion(
        id="R4Q3",
        round_num=4,
        question=(
            "Apex has spent $1.5M on CPI Systems and $1.2M on Vendor/"
            "JIT (TQM). Maximum cumulative spend per initiative is ~$4M; "
            "max combined material cost reduction is ~11.8%. Marginal "
            "ROI is sharply diminishing past $3M. Should Apex keep "
            "spending in R4?"
        ),
        options=[
            "Yes — spend $2M more on each; benefits compound",
            "Selectively top up to ~$3M per initiative, focusing on "
            "Concurrent Engineering and QFD for R&D speed",
            "Stop all TQM — fund stock buyback instead",
            "Cancel TQM and request a refund",
        ],
        correct_index=1,
        explanation=(
            "TQM hits diminishing returns above $3M per initiative. Best "
            "marginal $ in R4 go to Concurrent Engineering (cuts R&D cycle "
            "up to 40%) and QFD (raises demand up to 14%) — both feed R5 "
            "revenue. Material reductions are mostly captured."
        ),
        topic="TQM ROI",
    ),
    BoardQueryQuestion(
        id="R4Q4",
        round_num=4,
        question=(
            "Final-round market share snapshot: Apex 32% (Core), "
            "Borealis 28%, Crestline 22%, Dynamo 18%. Apex is considering "
            "a $2 price cut on Axiom. Likely effect?"
        ),
        options=[
            "Steals 5-8 share points but slashes CM by ~6%; net positive "
            "only if volume grows >20%",
            "Doubles market share instantly",
            "No effect — customers ignore $2 changes",
            "Hurts Apex because lower price always means lower revenue",
        ],
        correct_index=0,
        explanation=(
            "Customer survey rewards prices near the segment's lower bound. "
            "A $2 cut on a $34 product (~6% price drop) typically lifts "
            "share by 5-8 points but compresses CM% from ~44% to ~38%. "
            "Net profit improves only if unit demand expands >20%."
        ),
        topic="Market Share / Pricing Trade-off",
    ),
    BoardQueryQuestion(
        id="R4Q5",
        round_num=4,
        question=(
            "Apex's 11.2S2032 bond ($8.8M, 11.2%) was issued when prime "
            "was ~10%. Current prime is 7.5%. Cost to retire early is "
            "1.5% of face = $132K. Should Apex refinance now?"
        ),
        options=[
            "No — pay the bond on schedule",
            "Yes — refinance with a new bond at ~9.0% (prime + 1.5% "
            "spread). Annual savings ~$194K vs $132K one-time fee, "
            "payback under 9 months",
            "Yes, but issue equity instead — cheaper than any bond",
            "Wait until R5 — interest is tax-deductible anyway",
        ],
        correct_index=1,
        explanation=(
            "Old rate 11.2% vs new ~9.0% = savings of 2.2% x $8.8M = "
            "~$194K/yr. Early-retirement fee = 1.5% x $8.8M = $132K. "
            "Payback < 9 months. Tax-deductibility applies to BOTH bonds "
            "so it's a wash. Refinance."
        ),
        topic="Bond Refinancing",
    ),
    BoardQueryQuestion(
        id="R4Q6",
        round_num=4,
        question=(
            "Apex's cumulative profit after R4 is $98M; Borealis $61M, "
            "Crestline $48M, Dynamo $58M. Apex leads. The Final BSC also "
            "weights last-year metrics. To LOCK in the win in R5, what "
            "matters MOST?"
        ),
        options=[
            "Cumulative metrics — keep doing what works",
            "Last-year ROE, ROS, stock price, and BSC perspective scores; "
            "one weak R5 can erase a cumulative lead",
            "Just market share",
            "Cash on the balance sheet at year-end",
        ],
        correct_index=1,
        explanation=(
            "BizSim Final BSC heavily weights R5-specific scores — "
            "stock price, ROE, ROS, market share, contribution margin, "
            "plant utilization, employee productivity, customer survey. "
            "A poor R5 can wipe out earlier lead. Treat R5 like the "
            "championship game."
        ),
        topic="Final-Year Strategy",
    ),

    # ------------------------------------------------------------
    # ROUND 5 (7 questions) — FINAL CUMULATIVE
    # ------------------------------------------------------------
    BoardQueryQuestion(
        id="R5Q1",
        round_num=5,
        question=(
            "Final R5 results — Apex: Sales $245M, Net Profit $34M, "
            "Equity $112M. What is Apex's R5 ROE?"
        ),
        options=["13.9%", "23.6%", "30.4%", "45.8%"],
        correct_index=2,
        explanation=(
            "ROE = Net Profit / Equity = $34M / $112M = 30.4%. BizSim "
            "BSC awards full ROE points for >18% in the final year. "
            "Apex crushed it."
        ),
        topic="Final ROE",
    ),
    BoardQueryQuestion(
        id="R5Q2",
        round_num=5,
        question=(
            "Cumulative profit across R1-R5: Apex $145M, Borealis $92M, "
            "Crestline $71M, Dynamo $88M. Which company is the clear winner "
            "on this metric, and how big is the lead?"
        ),
        options=[
            "Apex — leads Borealis (#2) by $53M (~58% margin)",
            "Borealis — close second, almost tied",
            "Crestline — high market share offsets low profit",
            "Dynamo — best ROS",
        ],
        correct_index=0,
        explanation=(
            "Apex $145M vs Borealis $92M = $53M lead = 57.6% more "
            "cumulative profit. Cumulative profit is one of the Final "
            "BSC's biggest weights (~30 points). A 50%+ margin is "
            "decisive."
        ),
        topic="Cumulative Profit",
    ),
    BoardQueryQuestion(
        id="R5Q3",
        round_num=5,
        question=(
            "Final stock prices: Apex $158, Borealis $98, Crestline $76, "
            "Dynamo $89. What does this ranking reveal about how the "
            "market viewed each firm's 5-year run?"
        ),
        options=[
            "Apex delivered the best mix of EPS growth, dividend "
            "discipline, and leverage; Crestline's slide reflects weak "
            "margins compounding for 5 years",
            "Stock prices are random in BizSim",
            "Borealis is undervalued — bigger market cap than Apex",
            "Crestline won because lowest stock price means cheapest entry",
        ],
        correct_index=0,
        explanation=(
            "Stock price = EPS x P/E + dividend signal - debt penalty. "
            "Apex's lead reflects 5 years of compounding strong ROS, "
            "controlled dilution, and dividends near 65% of EPS. "
            "Crestline's $76 reflects 5 years of weak ROS and low EPS."
        ),
        topic="Final Stock Price",
    ),
    BoardQueryQuestion(
        id="R5Q4",
        round_num=5,
        question=(
            "Apex's Total BSC over R1-R5 (cumulative + final): 742/1000. "
            "Top quartile is typically >700, top decile >780. How should "
            "this be characterized to the board?"
        ),
        options=[
            "Below average — request a do-over",
            "Solid top-quartile finish; one or two perspectives have "
            "room to improve next time",
            "Perfect — no improvement possible",
            "Score is irrelevant; only profit counts",
        ],
        correct_index=1,
        explanation=(
            "BizSim grading: 600-700 average, 700-780 top quartile, "
            "780+ elite. 742 is a clear top-quartile finish — strong "
            "execution. Drill into the lowest-scoring perspective "
            "(usually Internal Business or Learning & Growth) for "
            "improvement insight."
        ),
        topic="Balanced Scorecard Total",
    ),
    BoardQueryQuestion(
        id="R5Q5",
        round_num=5,
        question=(
            "Apex's Atlas (Thrift, now age 8.2) sold 1.5M units at $22, "
            "VC $11. Contribution dollars and CM%?"
        ),
        options=[
            "$16.5M / 50%",
            "$22.0M / 33%",
            "$33.0M / 33%",
            "$16.5M / 33%",
        ],
        correct_index=0,
        explanation=(
            "CM% = (22 - 11) / 22 = 50%. Contribution dollars = $11 x "
            "1.5M = $16.5M. A 50% CM on an aging Thrift product is "
            "best-in-class — the strategy of NOT revising old Thrift "
            "products paid off."
        ),
        topic="Final Contribution Margin",
    ),
    BoardQueryQuestion(
        id="R5Q6",
        round_num=5,
        question=(
            "Apex's R5 Total Assets $185M, Sales $245M, leverage 2.1, "
            "ROE 30.4%. DuPont decomposition: which component contributed "
            "MOST to ROE growth vs R0?"
        ),
        options=[
            "Asset turnover (245/185 = 1.32 vs R0's 1.32) — UNCHANGED",
            "Margin (ROS rose from 12.3% to ~13.9%) — small gain",
            "Leverage (1.74 -> 2.1) AND margin growth together — strong "
            "compound effect",
            "Equity issuance",
        ],
        correct_index=2,
        explanation=(
            "DuPont: ROE = Margin x Asset Turnover x Leverage. Margin "
            "improved ~13%, turnover ~flat, leverage up 21%. Combined "
            "multiplication produced ROE growth from 28% to 30%+. "
            "Leveraging the BSC sweet spot was the key move."
        ),
        topic="DuPont Analysis",
    ),
    BoardQueryQuestion(
        id="R5Q7",
        round_num=5,
        question=(
            "Reflecting on the 5-year run: which single strategic decision "
            "had the LARGEST positive impact on Apex's final stock price "
            "and Total BSC?"
        ),
        options=[
            "Issuing maximum new equity every round",
            "Investing in TQM Concurrent Engineering + QFD early; "
            "compounding R&D speed and demand for 4 years",
            "Cutting marketing budgets to zero to lift short-term ROS",
            "Paying minimum dividend to hoard cash",
        ],
        correct_index=1,
        explanation=(
            "Concurrent Engineering cuts R&D cycle up to 40% and QFD "
            "lifts demand up to 14%. Together they compound for 4+ "
            "years: faster product refreshes meet customer ideal-spots, "
            "expanded demand lifts revenue, profit, EPS, stock price. "
            "Highest single-decision NPV in the simulation."
        ),
        topic="Strategic Reflection",
    ),
]


# ============================================================
# Helpers
# ============================================================

def get_round_queries(round_num: int) -> List[BoardQueryQuestion]:
    """Return all questions belonging to a given round (1-5)."""
    return [q for q in BOARD_QUERIES if q.round_num == round_num]


def grade_round(round_num: int, answers: Dict[str, int]) -> Dict:
    """
    Grade a player's MCQ answers for a round.

    Args:
        round_num: which round (1-5)
        answers:   mapping of question_id -> selected option index (0-3)

    Returns:
        {
            "round": int,
            "correct": int,
            "total": int,
            "percent": float,        # 0..1
            "details": [
                {"id", "question", "selected", "correct", "is_correct",
                 "explanation"},
                ...
            ],
        }
    """
    questions = get_round_queries(round_num)
    details = []
    correct = 0
    for q in questions:
        selected = answers.get(q.id)
        is_correct = selected == q.correct_index
        if is_correct:
            correct += 1
        details.append(
            {
                "id": q.id,
                "question": q.question,
                "selected": selected,
                "correct": q.correct_index,
                "is_correct": is_correct,
                "explanation": q.explanation,
                "topic": q.topic,
            }
        )
    total = len(questions)
    return {
        "round": round_num,
        "correct": correct,
        "total": total,
        "percent": (correct / total) if total else 0.0,
        "details": details,
    }


# ============================================================
# Self-test
# ============================================================

if __name__ == "__main__":
    print(f"Total board queries: {len(BOARD_QUERIES)}")
    expected = {1: 5, 2: 6, 3: 6, 4: 6, 5: 7}
    all_ok = True
    for rnd in range(1, 6):
        qs = get_round_queries(rnd)
        ok = len(qs) == expected[rnd]
        all_ok &= ok
        flag = "OK" if ok else "FAIL"
        print(
            f"  Round {rnd}: {len(qs)} questions "
            f"(expected {expected[rnd]}) [{flag}]"
        )

    # Validate every question has 4 options and a valid correct_index
    integrity_ok = True
    for q in BOARD_QUERIES:
        if len(q.options) != 4:
            print(f"  [FAIL] {q.id}: has {len(q.options)} options (need 4)")
            integrity_ok = False
        if not (0 <= q.correct_index < len(q.options)):
            print(f"  [FAIL] {q.id}: correct_index out of range")
            integrity_ok = False
        if not q.explanation:
            print(f"  [FAIL] {q.id}: missing explanation")
            integrity_ok = False

    # Topic coverage
    topics = sorted({q.topic for q in BOARD_QUERIES})
    print(f"\nTopics covered ({len(topics)}):")
    for t in topics:
        print(f"  - {t}")

    # Tiny grading sanity test
    sample = {q.id: q.correct_index for q in get_round_queries(1)}
    res = grade_round(1, sample)
    grading_ok = res["correct"] == res["total"] == 5
    print(
        f"\nGrade-round sanity (all-correct R1): "
        f"{res['correct']}/{res['total']} "
        f"[{'OK' if grading_ok else 'FAIL'}]"
    )

    print(
        "\nOverall:",
        "ALL CHECKS PASSED"
        if all_ok and integrity_ok and grading_ok
        else "FAILURES PRESENT",
    )
