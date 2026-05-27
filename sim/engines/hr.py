"""
HR engine — OLD Comp-XM version (3 decisions per company per round).

Per Capsim HR Guide:
  - Workforce Complement: Total employees needed (entered on Production page)
    Each unit of production needs ~0.0007 employees (approximate)
  - Recruit Spend: $0-$5,000 per new employee above auto $1,000
    Higher spend -> better talent -> productivity gain
  - Training Hours: 0-80 hours/employee/year × $20/hour
    Higher training -> productivity gain + turnover reduction

  - Productivity Index: 1.0 baseline, can reach ~1.18 with full HR
  - Turnover Rate: 10% default, drops to ~5% with high training
  - Annual Raise: ~5% in labor contract (default)

Reference: Capsim HR Guide
"""
from __future__ import annotations
from typing import Dict
from sim.data_models import Company, HRState


# Constants
AUTO_RECRUIT_COST = 1000          # $/new employee (automatic)
TRAINING_COST_PER_HOUR = 20       # $/hour/employee
MAX_RECRUIT_SPEND = 5000          # $/employee additional
MAX_TRAINING_HOURS = 80
BASE_TURNOVER = 0.10              # 10% baseline
WAGE_PER_EMPLOYEE = 25530         # $/yr base wage
BENEFITS_PER_EMPLOYEE = 2500      # $/yr


def employees_needed(company: Company) -> int:
    """
    Estimate employees needed from total production units (thousands).
    Calibrated to Andrews R0: 804 employees / 5594 unit-thousands ≈ 0.144.
    """
    total_production = sum(p.production_schedule for p in company.products)
    return max(50, int(total_production * 0.144))


def productivity_index(recruit_spend: float, training_hours: int) -> float:
    """
    Productivity factor based on HR spend.
    No HR: 1.0
    Max HR ($5K + 80hr): ~1.18 (18% productivity gain)
    """
    recruit_factor = min(1.0, recruit_spend / MAX_RECRUIT_SPEND)
    training_factor = min(1.0, training_hours / MAX_TRAINING_HOURS)
    # Each factor contributes up to 9% productivity gain
    return 1.0 + 0.09 * recruit_factor + 0.09 * training_factor


def turnover_rate(training_hours: int) -> float:
    """Training reduces turnover. Max training cuts turnover from 10% to 5%."""
    training_factor = min(1.0, training_hours / MAX_TRAINING_HOURS)
    return BASE_TURNOVER - 0.05 * training_factor


def recruiting_cost(new_employees: int, recruit_spend: float) -> float:
    """Total recruiting cost = new_emp × (auto $1K + extra spend)."""
    return new_employees * (AUTO_RECRUIT_COST + recruit_spend)


def training_cost(complement: int, training_hours: int) -> float:
    """Total training cost = employees × hours × $20."""
    return complement * training_hours * TRAINING_COST_PER_HOUR


def separation_cost(separated_employees: int) -> float:
    """Cost to lay off employees: 0 for natural turnover."""
    return 0.0  # Capsim has separation cost only for forced layoffs (not modeled)


def labor_wages_total(complement: int) -> float:
    """Total wages + benefits."""
    return complement * (WAGE_PER_EMPLOYEE + BENEFITS_PER_EMPLOYEE)


def update_hr(company: Company, recruit_spend: float, training_hours: int) -> Dict:
    """
    Apply HR decisions for the round. Updates company.hr.
    Returns summary dict.
    """
    needed = employees_needed(company)
    current = company.hr.workforce_complement

    new_pi = productivity_index(recruit_spend, training_hours)
    new_turnover = turnover_rate(training_hours)

    # Employees that turn over this year
    separated = int(current * new_turnover)
    # New hires to maintain + grow complement
    new_hires = max(0, needed - (current - separated))

    rec_cost = recruiting_cost(new_hires, recruit_spend)
    train_cost = training_cost(needed, training_hours)
    total_admin = rec_cost + train_cost

    company.hr = HRState(
        workforce_complement=needed,
        needed_complement=needed,
        first_shift_complement=min(needed, employees_needed_first_shift(company)),
        second_shift_complement=max(0, needed - employees_needed_first_shift(company)),
        overtime_pct=0.0,
        turnover_rate=new_turnover,
        new_employees=new_hires,
        separated_employees=separated,
        recruit_spend=recruit_spend,
        training_hours=training_hours,
        productivity_index=new_pi,
        recruiting_cost=rec_cost,
        separation_cost=0,
        training_cost=train_cost,
        total_hr_admin_cost=total_admin,
    )

    return {
        "needed_complement": needed,
        "new_hires": new_hires,
        "separated": separated,
        "recruit_cost": rec_cost,
        "training_cost": train_cost,
        "total_hr_admin": total_admin,
        "productivity_index": new_pi,
        "turnover_rate": new_turnover,
    }


def employees_needed_first_shift(company: Company) -> int:
    """How many employees needed if all on 1st shift only."""
    cap = sum(p.capacity_first_shift for p in company.products)
    return int(cap * 0.144)


def labor_cost_adjustment(productivity_index: float) -> float:
    """
    Multiplier on labor cost from productivity.
    Higher PI -> lower effective labor cost (same wages, more output).
    """
    return 1.0 / max(0.5, productivity_index)


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    print("=== HR Module demo ===\n")

    andrews = state.get_company("Andrews")
    print(f"Andrews current PI: {andrews.hr.productivity_index:.3f}")
    print(f"Employees needed (estimated): {employees_needed(andrews)}")

    print("\nHR investment scenarios:")
    for rspend, thours in [(0, 0), (2500, 40), (5000, 80)]:
        pi = productivity_index(rspend, thours)
        to = turnover_rate(thours)
        # Cost: assume 800 employees
        cost = recruiting_cost(140, rspend) + training_cost(800, thours)
        print(f"  Recruit ${rspend}/Train {thours}hr -> PI {pi:.3f}, Turnover {to*100:.1f}%, Cost ${cost/1000:.0f}K")
