"""
Production engine.

CAPSIM UNIT CONVENTION (IMPORTANT):
  - `units`, `capacity`, `inventory`, `production_schedule` are integers in THOUSANDS of units.
    e.g., capacity_first_shift=1130 means 1,130,000 units of capacity.
  - `price`, `material_cost`, `labor_cost` are in DOLLARS per ACTUAL unit.
  - Revenue = units(thousands) * price($/unit) = $thousands -> multiply by 1000 for full $.

Per Capsim:
  - Plant capacity cost = $6 (base) + $4 × automation_level per 1000-unit of 1st-shift cap.
    For 1130 capacity (1.13M units): cost = 1130 × ($6 + $4×6) × 1000 = $33.9M
  - 1st shift labor = base labor cost × productivity_index
  - 2nd shift labor = 1st shift × 1.5 (50% premium)
  - Each +1 automation level reduces labor cost by ~10% (level 1 = 100% labor,
    level 10 = ~10% labor)
  - Maximum 200% utilization (1 shift = 100%, 2 shifts = 200%)
  - Plant depreciation: 15-year straight line
  - Inventory carry cost: 12% of cost per year on average inventory

Reference: Capstone User Guide §4.3 Production
"""
from __future__ import annotations
from typing import Dict
from sim.data_models import Product, Company, GameState


# Constants
BASE_CAPACITY_COST_PER_UNIT = 6.0       # $ per 1st-shift unit
AUTOMATION_COST_PER_LEVEL = 4.0         # $ per unit per automation level
SECOND_SHIFT_LABOR_MULTIPLIER = 1.5
INVENTORY_CARRY_PCT = 0.12              # of unit cost per year
DEPRECIATION_YEARS = 15
MAX_UTILIZATION = 2.0                   # 200% = 2 shifts


def labor_cost_factor(automation: float, productivity_index: float = 1.0) -> float:
    """
    Labor cost multiplier given automation level (1.0-10.0) and HR productivity.
    Automation 1 = 1.00, Automation 10 = 0.10 (approximate -10% per level)
    """
    auto_factor = max(0.10, 1.0 - (automation - 1.0) * 0.10)
    return auto_factor / max(0.5, productivity_index)


def compute_unit_labor(base_labor: float, automation: float, productivity_index: float = 1.0,
                       second_shift_fraction: float = 0.0) -> float:
    """Per-unit labor cost given automation, productivity, and 2nd-shift fraction."""
    first_shift_labor = base_labor * labor_cost_factor(automation, productivity_index)
    if second_shift_fraction <= 0:
        return first_shift_labor
    second_shift_labor = first_shift_labor * SECOND_SHIFT_LABOR_MULTIPLIER
    return first_shift_labor * (1 - second_shift_fraction) + second_shift_labor * second_shift_fraction


def capacity_purchase_cost(units_thousands: int, automation: float) -> float:
    """
    Cost in DOLLARS to buy `units_thousands` of 1st-shift capacity at given automation.
    units_thousands = capacity in 1000s (matching Inquirer convention).
    """
    return units_thousands * (BASE_CAPACITY_COST_PER_UNIT + AUTOMATION_COST_PER_LEVEL * automation) * 1000


def automation_upgrade_cost(units_thousands: int, old_auto: float, new_auto: float) -> float:
    """Cost in DOLLARS to upgrade automation from old to new level."""
    if new_auto <= old_auto:
        return 0.0
    return units_thousands * AUTOMATION_COST_PER_LEVEL * (new_auto - old_auto) * 1000


def capacity_sell_value(units_thousands: int, automation: float, depreciation_pct: float = 0.30) -> float:
    """Dollars received from selling capacity (default 30% of original cost)."""
    original_cost = capacity_purchase_cost(units_thousands, automation)
    return original_cost * depreciation_pct


def plant_value(product: Product) -> float:
    """Current gross plant value in DOLLARS for this product line."""
    return capacity_purchase_cost(product.capacity_first_shift, product.automation)


def annual_depreciation(product: Product) -> float:
    """Annual depreciation in dollars: gross plant / 15 years."""
    return plant_value(product) / DEPRECIATION_YEARS


def schedule_production(product: Product, requested_units: int) -> Dict:
    """
    Compute production schedule details.

    Returns dict with:
      first_shift_units, second_shift_units, utilization_pct,
      total_labor_cost, total_material_cost, total_production
    """
    cap = product.capacity_first_shift
    max_units = int(cap * MAX_UTILIZATION)
    actual = min(max(0, requested_units), max_units)

    first_shift = min(actual, cap)
    second_shift = max(0, actual - cap)
    util_pct = (actual / cap) * 100 if cap > 0 else 0

    # Per-unit costs (assuming no TQM/HR adjustments here - applied by round engine)
    first_labor = product.labor_cost * labor_cost_factor(product.automation)
    second_labor = first_labor * SECOND_SHIFT_LABOR_MULTIPLIER

    # NOTE: units are in thousands; multiply by 1000 to get DOLLARS from $/unit × units(thousands)
    total_labor = (first_shift * first_labor + second_shift * second_labor) * 1000
    total_material = actual * product.material_cost * 1000

    return {
        "scheduled": actual,
        "first_shift_units": first_shift,
        "second_shift_units": second_shift,
        "utilization_pct": util_pct,
        "total_labor_cost": total_labor,                    # $
        "total_material_cost": total_material,              # $
        "total_production_cost": total_labor + total_material,
        "unit_cost_first_shift": product.material_cost + first_labor,    # $/unit
        "unit_cost_second_shift": product.material_cost + second_labor,
    }


def inventory_carry_cost(product: Product, avg_inventory_units_thousands: int) -> float:
    """Annual cost in DOLLARS to carry inventory: 12% of unit cost × units."""
    unit_cost = product.material_cost + product.labor_cost * labor_cost_factor(product.automation)
    return avg_inventory_units_thousands * unit_cost * INVENTORY_CARRY_PCT * 1000


def company_production_summary(company: Company) -> Dict:
    """Aggregate production stats for a company."""
    total_units = 0
    total_capacity = 0
    total_labor_cost = 0
    total_material_cost = 0
    for p in company.products:
        sched = schedule_production(p, p.production_schedule)
        total_units += sched["scheduled"]
        total_capacity += p.capacity_first_shift
        total_labor_cost += sched["total_labor_cost"]
        total_material_cost += sched["total_material_cost"]
    return {
        "total_units_scheduled": total_units,
        "total_1st_shift_capacity": total_capacity,
        "avg_utilization_pct": (total_units / total_capacity * 100) if total_capacity > 0 else 0,
        "total_labor_cost": total_labor_cost,
        "total_material_cost": total_material_cost,
    }


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    andrews = state.get_company("Andrews")
    print("=== Andrews R0 production analysis ===")
    for p in andrews.products:
        # Simulate producing at 150% utilization
        target = int(p.capacity_first_shift * 1.5)
        sched = schedule_production(p, target)
        print(f"\n{p.name} (auto {p.automation}, cap {p.capacity_first_shift}):")
        print(f"  Schedule {target} units = {sched['utilization_pct']:.0f}% util")
        print(f"  1st shift: {sched['first_shift_units']} @ ${sched['unit_cost_first_shift']:.2f}/unit")
        print(f"  2nd shift: {sched['second_shift_units']} @ ${sched['unit_cost_second_shift']:.2f}/unit")
        print(f"  Total labor ${sched['total_labor_cost']/1000:.0f}K + material ${sched['total_material_cost']/1000:.0f}K")

    # Plant value check
    total_plant = sum(plant_value(p) for p in andrews.products)
    print(f"\nAndrews total plant value: ${total_plant/1e6:.1f}M (Inquirer says $96.8M)")
