"""
TQM engine — 10 initiatives, S-curve response, cap $2M/initiative/round, $4M cumulative.

Per CompMastery TQM model:
  Process Management initiatives:
    - CPI Systems (Continuous Process Improvement) -> material -3% to -5%
    - Vendor/JIT -> material -3% to -5%
    - Quality Initiative Training (QIT) -> labor -2% to -4%
    - Channel Support Systems -> demand +1% to +2%
    - Concurrent Engineering -> R&D cycle time -20% to -40%
    - UNEP Green Programs -> admin -1% to -2%

  Sustainability/CSR initiatives:
    - GEMI TQEM Sustainability -> material -3% to -5%, demand +2% to +3%
    - Benchmarking -> admin -2% to -3%, R&D cycle -10% to -20%
    - Quality Function Deployment (QFD) -> demand +6% to +8% [BEST ROI]
    - CCE/6 Sigma Training -> labor -7% to -14%, material -7% to -8%

  Max cumulative impacts:
    - Material -11.8%
    - Labor -14%
    - R&D cycle -40%
    - Admin -60%
    - Demand +14.4%

  S-curve: $0 = no impact, $1M = ~half impact, $2M = ~full impact per round
           $4M cumulative cap per initiative

Reference: CompMastery TQM model
"""
from __future__ import annotations
from typing import Dict
from sim.data_models import Company, TQMState


# Per-initiative max impact (full effect at $4M cumulative)
TQM_IMPACTS = {
    # Initiative → effect mapping follows the CompMastery specification §7.1:
    #   UNEP Green   = ↑Demand + ↓Material (was: ↓Admin — wrong lever entirely)
    #   Benchmarking = ↓Admin ONLY         (was: also ↓R&D cycle — that belongs to QFD)
    #   QFD Effort   = ↓R&D cycle + ↑Demand (was: ↑Demand only — missing its cycle-time cut)
    # Aggregate ceilings below are unchanged (rd_cycle still reaches −40% via CE+QFD).
    "CPI Systems":              {"material": -0.04, "labor": 0, "rd_cycle": 0, "admin": 0, "demand": 0},
    "Vendor/JIT":               {"material": -0.04, "labor": 0, "rd_cycle": 0, "admin": 0, "demand": 0},
    "QIT":                      {"material": 0, "labor": -0.03, "rd_cycle": 0, "admin": 0, "demand": 0},
    "Channel Support Systems":  {"material": 0, "labor": 0, "rd_cycle": 0, "admin": 0, "demand": +0.015},
    "Concurrent Engineering":   {"material": 0, "labor": 0, "rd_cycle": -0.30, "admin": 0, "demand": 0},
    "UNEP Green Programs":      {"material": -0.015, "labor": 0, "rd_cycle": 0, "admin": 0, "demand": +0.015},
    "GEMI TQEM":                {"material": -0.04, "labor": 0, "rd_cycle": 0, "admin": 0, "demand": +0.025},
    "Benchmarking":             {"material": 0, "labor": 0, "rd_cycle": 0, "admin": -0.025, "demand": 0},
    "QFD Effort":               {"material": 0, "labor": 0, "rd_cycle": -0.15, "admin": 0, "demand": +0.045},
    "CCE/6 Sigma":              {"material": -0.075, "labor": -0.105, "rd_cycle": 0, "admin": 0, "demand": 0},
}

INITIATIVE_NAMES = list(TQM_IMPACTS.keys())

# Sweet spot: $1.5M per initiative per round
TQM_FULL_EFFECT_CUMULATIVE = 4_000_000   # $ cumulative cap per initiative
TQM_PER_ROUND_CAP = 2_000_000             # $ per initiative per round


def s_curve_factor(cumulative_spend: float, cap: float = TQM_FULL_EFFECT_CUMULATIVE) -> float:
    """
    S-curve response: 0 at $0, ~0.5 at $1.5M, ~0.9 at $3M, 1.0 at $4M+.

    Approximation: 1 - exp(-3 × x/cap)
    """
    if cumulative_spend <= 0:
        return 0.0
    if cumulative_spend >= cap:
        return 1.0
    import math
    return 1.0 - math.exp(-3.0 * cumulative_spend / cap)


def update_tqm(company: Company, spend_per_initiative: Dict[str, float]) -> Dict:
    """
    Apply TQM spending for the round. Updates company.tqm cumulative + impacts.

    spend_per_initiative: {initiative_name: $ this round}
    Cap each at $2M per round; clamp invalid names.
    """
    tqm = company.tqm
    spend_this_round: Dict[str, float] = {}
    total_round_spend = 0

    for name, amount in spend_per_initiative.items():
        if name not in TQM_IMPACTS:
            continue
        # Cap at per-round max
        amt = max(0, min(amount, TQM_PER_ROUND_CAP))
        # ALSO cap at cumulative max — don't waste $ above $4M per initiative
        already_spent = tqm.cumulative_spend.get(name, 0)
        max_more = max(0, TQM_FULL_EFFECT_CUMULATIVE - already_spent)
        amt = min(amt, max_more)
        spend_this_round[name] = amt
        tqm.cumulative_spend[name] = already_spent + amt
        total_round_spend += amt

    tqm.spend_this_round = spend_this_round
    tqm.total_expenditures += total_round_spend

    # Recompute cumulative impacts (all initiatives stack)
    mat = lab = rd = adm = dem = 0.0
    for name, impacts in TQM_IMPACTS.items():
        cum = tqm.cumulative_spend.get(name, 0)
        if cum <= 0:
            continue
        factor = s_curve_factor(cum)
        mat += impacts["material"] * factor
        lab += impacts["labor"] * factor
        rd  += impacts["rd_cycle"] * factor
        adm += impacts["admin"] * factor
        dem += impacts["demand"] * factor

    # Cap at CompMastery maximums
    tqm.material_cost_reduction = max(-0.118, mat)
    tqm.labor_cost_reduction = max(-0.14, lab)
    tqm.rd_cycle_time_reduction = max(-0.40, rd)
    tqm.admin_cost_reduction = max(-0.60, adm)
    tqm.demand_increase = min(0.144, dem)

    return {
        "round_spend": total_round_spend,
        "cumulative_spend_total": sum(tqm.cumulative_spend.values()),
        "material_impact_pct": tqm.material_cost_reduction * 100,
        "labor_impact_pct": tqm.labor_cost_reduction * 100,
        "rd_cycle_impact_pct": tqm.rd_cycle_time_reduction * 100,
        "admin_impact_pct": tqm.admin_cost_reduction * 100,
        "demand_impact_pct": tqm.demand_increase * 100,
    }


def recommended_initiatives_for_round(round_num: int) -> Dict[str, float]:
    """
    Recommended TQM allocation by round (from the Playbook).
    R1: full $1.5M each on 6 high-ROI initiatives = $9M
    R2: same set, refresh = $9M
    R3: maintenance $1M each on 4 = $4M
    R4: only QFD $1.5M = $1.5M (most ROI in last round)
    """
    if round_num == 1:
        return {
            "QFD Effort": 1_500_000,
            "CCE/6 Sigma": 1_500_000,
            "Vendor/JIT": 1_500_000,
            "CPI Systems": 1_500_000,
            "Concurrent Engineering": 1_500_000,
            "GEMI TQEM": 1_500_000,
        }
    if round_num == 2:
        return {
            "QFD Effort": 1_500_000,
            "CCE/6 Sigma": 1_500_000,
            "Vendor/JIT": 1_500_000,
            "Concurrent Engineering": 1_000_000,
            "GEMI TQEM": 1_500_000,
            "Channel Support Systems": 1_000_000,
        }
    if round_num == 3:
        return {
            "QFD Effort": 1_000_000,
            "CCE/6 Sigma": 1_000_000,
            "Benchmarking": 1_000_000,
            "Channel Support Systems": 1_000_000,
        }
    if round_num == 4:
        return {"QFD Effort": 1_500_000}
    return {}


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    apex = state.get_company("Apex")
    print("=== TQM 4-round projection (Conservative R4 strategy) ===\n")
    for r in range(1, 5):
        rec = recommended_initiatives_for_round(r)
        total = sum(rec.values())
        result = update_tqm(apex, rec)
        print(f"R{r}: spend ${total/1e6:.1f}M on {list(rec.keys())}")
        print(f"  Cumulative ${result['cumulative_spend_total']/1e6:.1f}M")
        print(f"  Impacts: material {result['material_impact_pct']:.1f}%, labor {result['labor_impact_pct']:.1f}%, "
              f"R&D cycle {result['rd_cycle_impact_pct']:.1f}%, admin {result['admin_impact_pct']:.1f}%, demand {result['demand_impact_pct']:.1f}%\n")
