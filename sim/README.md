# Comp-XM 2026 Simulator — Andrews Edition

A Python replica of Capsim's Comp-XM 2026 business simulation, built for exam preparation.

**Player**: Andrews Corporation (you) vs Baldwin / Chester / Digby (AI)
**Goal**: Maximize Balanced Scorecard total (1000 pts) across 4 rounds + final cumulative

---

## Quick Start

```bash
# 1. From F:\Claude CODE\CAPSIM\
cd F:\Claude CODE\CAPSIM

# 2. Install dependencies (already done if you ran the setup)
pip install streamlit pydantic pandas plotly pytest

# 3. Run the Streamlit web app
streamlit run sim/app.py
```

Open `http://localhost:8501` in your browser.

---

## Features

### Modules implemented
- **R&D**: project time, position move cost, MTBF change, age halves on revise
- **Marketing**: classic Promo + Sales (Comp-XM does NOT use Advanced Marketing Module)
- **Production**: capacity cost ($6 + $4×automation), 2nd shift +50%, 200% max utilization
- **Finance**: Income Statement, Balance Sheet, Cash Flow, bonds (5% brokerage, 80% plant cap), stock issue/buyback, dividend, credit rating
- **HR (OLD Comp-XM)**: Recruit Spend $0-5K + Training 0-80hr × $20 + Workforce Complement (on Production)
- **TQM**: 10 initiatives, S-curve, $4M cumulative cap, $2M per round cap
- **AI Competitors**:
  - Baldwin: Niche High Tech (Nano + Elite focus, premium pricing)
  - Chester: Niche Low Tech (Thrift + Core focus, low pricing, high automation)
  - Digby: Broad (all 4 segments, max HR)
- **BSC Scoring**: 4 perspectives + final cumulative (approximate weights)
- **Inquirer**: Front page, Stocks/Bonds, Segments, Production, Market Share, HR/TQM, Annual Reports
- **Board Queries**: 30 MCQ across 5 rounds (auto-graded with explanations)

### UI Pages
1. **🏠 Dashboard** — overview, perceptual map, KPIs
2. **📝 Decisions (R&D/Mkt/Prod)** — per-product decision forms
3. **💰 Finance/HR/TQM** — bonds, dividend, HR sliders, TQM allocator
4. **📰 Comp-XM Inquirer** — full newsletter
5. **❓ Board Queries** — MCQ practice
6. **📊 Balanced Scorecard** — round + cumulative
7. **📈 History & Trends** — round-by-round charts
8. **⚙️ Settings** — save/reset

---

## Architecture

```
sim/
├── __init__.py
├── app.py                      # Streamlit UI
├── data_models.py              # Pydantic schemas (Segment, Product, Company, Bond, etc.)
├── ai_competitors.py           # Baldwin/Chester/Digby decision logic
├── board_queries.py            # 30 MCQ questions
├── data/
│   ├── __init__.py
│   └── r0_seed.py              # R0 starting state from Comp-XM Inquirer 2026
├── engines/
│   ├── __init__.py
│   ├── customer_score.py       # Customer survey + weighted score
│   ├── demand.py               # Segment drift + demand allocation
│   ├── production.py           # Capacity, automation, labor
│   ├── rd.py                   # R&D project mechanics
│   ├── marketing.py            # Awareness/Accessibility curves
│   ├── finance.py              # IS/BS/CF + bonds + ratios
│   ├── hr.py                   # OLD Comp-XM 3-decision HR
│   ├── tqm.py                  # 10 TQM initiatives + S-curve
│   ├── bsc.py                  # Balanced Scorecard scoring
│   └── round_engine.py         # Round orchestrator
├── reports/
│   ├── __init__.py
│   └── inquirer.py             # Comp-XM newsletter generator
└── tests/
    ├── __init__.py
    └── test_integration_4round.py
```

---

## Data Sources

R0 state is loaded from official Comp-XM 2026 reports in `F:\Claude CODE\CAPSIM\`:
- **Comp-XM - Industry Conditions Report 2026** → segments, drift vectors, growth rates, buying criteria
- **Comp-XM - Inquirer Report 2026 R0** → company financials, product positions, bonds, market share

---

## Limitations vs Real Comp-XM

| Feature | Status |
|---|---|
| Customer survey formula | ✅ Public Capsim formula |
| Segment drift + growth | ✅ Official R0 data |
| Production cost | ✅ Public formula |
| Bond pricing | ✅ Approximated |
| BSC weights | ⚠️ APPROXIMATE (Capsim proprietary; off by ±20%) |
| AI competitor behavior | ⚠️ Rule-based, not adaptive (real Capsim is deterministic too) |
| Random events (recession, lawsuit) | ❌ Not modeled |
| Stock price formula | ⚠️ Approximate (BV + 5×EPS + 10×Div) |
| Sales Forecast accuracy effect | ⚠️ Simplified |

---

## Validation against R0 data

| Metric | Simulator | Inquirer | Match? |
|---|---|---|---|
| Andrews Sales | $163.3M | $163.3M | ✅ |
| Andrews ROS | 12.3% | 12.3% | ✅ |
| Andrews ROE | 28.3% | 28.3% | ✅ |
| Andrews Stock | $95.38 | $95.38 | ✅ |
| Andrews Plant | $96.8M | $96.8M | ✅ |
| Andrews Bonds | $27.2M | $27.2M | ✅ |
| Industry Total | 18,901 | 18,902 | ✅ |
| Thrift R0 demand | 5,101 | 5,101 | ✅ |
| Andrews Thrift share | 14.3% (sim model) | 16% (Inquirer) | ⚠️ ~10% diff |

---

## Run Tests

```bash
cd F:\Claude CODE\CAPSIM
python -m pytest sim/tests/ -v
python -m sim.tests.test_integration_4round   # end-to-end 4-round playthrough
```

---

## Example Baseline Score

Using default sensible decisions (revise all, $1.5M Promo, $1.5M Sales, max premium pricing, Conservative TQM, $2500 + 40hr HR, retire 13.5S2027):

| Round | Stock | Profit | BSC |
|---|---|---|---|
| R1 | $110.67 | $7.5M | 82.8 |
| R2 | $124.75 | $13.1M | 83.7 |
| R3 | $91.05 | $7.6M | 71.5 |
| R4 | $92.88 | $8.4M | 70.1 |
| **TOTAL** | | $36.6M cum | **594.8/1000** |

**Passing score**: ~662 (50th percentile). Try better decisions to push higher!

---

## How to Practice for the Real Exam

1. **Read Comp-XM Industry Conditions Report 2026** (in `F:\Claude CODE\CAPSIM\`) to understand R0
2. **Use the Streamlit simulator** to test "what if" scenarios:
   - What if I price Attic at $20 instead of $26?
   - What if I retire all bonds in R1?
   - What if I skip TQM in R4?
3. **Practice Board Queries** — the MCQ bank covers all common Comp-XM topics
4. **Track BSC trends** — Stock + Profit + Customer score are the biggest drivers
5. **Read the Andrews Playbook** (`CompXM_2026_Andrews_Playbook.pdf`) alongside

---

## Limitations to Remember on Exam Day

- This simulator's BSC weights are approximate — real Capsim may score differently
- AI competitors here use fixed strategies — real Baldwin/Chester/Digby behavior may differ
- Use this as a **practice tool**, not a perfect predictor
- The actual exam runs on Capsim's servers; this only simulates the logic
