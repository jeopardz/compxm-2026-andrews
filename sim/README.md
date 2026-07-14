# CompMastery

CompMastery is an interactive business-strategy simulator. The player manages Apex
across four decision rounds while competing against three computer-controlled
companies: Borealis, Crestline, and Dynamo.

The objective is to build a resilient company and maximize the Balanced
Scorecard through coordinated R&D, marketing, production, finance, people, and
quality decisions.

## Quick start

Run these commands from the repository root:

```bash
python -m pip install -r requirements.txt
streamlit run sim/app.py
```

Then open `http://localhost:8501`.

## Companies and products

| Company | Products |
|---|---|
| Apex (player) | Atlas, Axiom, Arc, Aura |
| Borealis | Beacon, Brio, Bloom, Bolt |
| Crestline | Cedar, Coda, Crest, Cove |
| Dynamo | Delta, Dune, Drift, Dusk |

## Features

- R&D projects with position, reliability, age, cost, and completion-time effects
- Marketing decisions for price, promotion, sales, awareness, and accessibility
- Production planning for capacity, automation, inventory, labor, and utilization
- Finance decisions for debt, bonds, shares, dividends, cash flow, and credit rating
- People and quality investments with cumulative operational effects
- Rule-based computer competitors with distinct strategies
- Balanced Scorecard results and round-by-round history
- Deterministic scenario generation with Easy, Normal, and Hard variants
- Pre-validation of generated scenarios through structural and four-round checks
- Local play plus optional authentication, persistence, and billing integrations

## Application pages

1. Dashboard
2. R&D, marketing, and production decisions
3. Finance, people, and quality decisions
4. Industry newsletter and annual reports
5. Board questions
6. Balanced Scorecard
7. History and trends
8. Settings and saved games

## Architecture

```text
sim/
|-- app.py                  # Streamlit user interface
|-- data_models.py          # Core state and decision schemas
|-- ai_competitors.py       # Borealis/Crestline/Dynamo strategies
|-- board_queries.py        # Board-question bank
|-- data/
|   |-- r0_seed.py          # Reference starting state
|   |-- scenarios.py        # Deterministic scenario generation
|   |-- scenario_validator.py
|   `-- scenario_pool.py
|-- engines/
|   |-- customer_score.py
|   |-- demand.py
|   |-- production.py
|   |-- rd.py
|   |-- marketing.py
|   |-- finance.py
|   |-- hr.py
|   |-- tqm.py
|   |-- bsc.py
|   `-- round_engine.py
|-- reports/
|   `-- market_report.py
`-- tests/
```

## Scenario model

Every generated board is deterministic: rebuilding the same scenario ID yields
the same starting state. Before a scenario enters the playable pool, validation
checks that:

- financial statements remain balanced;
- products and market parameters are structurally valid;
- segment drift stays within the perceptual map;
- a complete four-round baseline playthrough does not crash;
- companies remain solvent and every segment retains demand; and
- baseline performance falls within a useful difficulty range.

## Run tests

```bash
python -m pytest sim/tests -v
python -m sim.tests.test_integration_4round
```

## Model limitations

CompMastery is an educational decision model rather than a forecast of real company
performance. Several equations, competitor strategies, market events, and
Balanced Scorecard weights are intentionally simplified or approximated. Use
results to compare strategies inside CompMastery, not as financial advice or as a
guarantee of outcomes in another simulation.
