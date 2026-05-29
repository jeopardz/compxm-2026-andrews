"""
Finance engine — Income Statement, Balance Sheet, Cash Flow, Bonds.

Per Capsim:
  - Income tax = 35% flat
  - Profit sharing = 1% of net profit (after tax)
  - Bond: 10-year term, 5% brokerage fee on issuance
  - New bond rate = current LT interest rate + 1.4% spread
  - Max bond debt = 80% × gross plant value
  - Current debt rate ≈ prime + 0.5% (short-term)
  - Emergency loan rate = current debt rate + 7.5% penalty
  - Stock issuance: $500K fee + commissions
  - Stock buyback: at current market price
  - Bond early retirement: 1.5% fee + premium over face

Reference: Capstone User Guide §4.5 Finance
"""
from __future__ import annotations
from typing import List, Optional, Dict
from sim.data_models import Company, Bond, Product, FinanceDecision
from sim.engines.production import plant_value, annual_depreciation, inventory_carry_cost, labor_cost_factor


# Constants
TAX_RATE = 0.35                 # 35% of pre-tax income (verified: all 4 cos in 2026 Inquirer = 35.0%)
PROFIT_SHARING_RATE = 0.02      # 2.0% of AFTER-TAX profit (back-calc from real 2026 Inquirer: 410/20511,
                                #   226/11280, 152/7611, 208/10413 all = 2.0%). NOT 1%, NOT 15%.
BOND_BROKERAGE_FEE = 0.05       # 5% on issuance
BOND_NEW_SPREAD = 0.014         # +1.4% over current rate
BOND_TERM_YEARS = 10
MAX_BOND_DEBT_RATIO = 0.80      # max bond debt as fraction of plant value
EMERGENCY_LOAN_PENALTY = 0.075  # +7.5% over current debt rate
EARLY_RETIRE_FEE = 0.015        # 1.5% of face value
STOCK_ISSUE_FEE = 500_000


def short_term_rate(prime_rate: float) -> float:
    return prime_rate + 0.005


def long_term_rate(prime_rate: float, sp_rating: str = "BB") -> float:
    """LT rate depends on credit rating. AAA = prime+1%, lower = more spread."""
    spread_by_rating = {
        "AAA": 0.010, "AA": 0.015, "A": 0.020, "BBB": 0.030,
        "BB": 0.040, "B": 0.055, "CCC": 0.075, "CC": 0.090,
        "C": 0.110, "DDD": 0.130, "DD": 0.150, "D": 0.180,
    }
    return prime_rate + spread_by_rating.get(sp_rating, 0.060)


def emergency_loan_rate(prime_rate: float) -> float:
    return short_term_rate(prime_rate) + EMERGENCY_LOAN_PENALTY


def bond_market_price(bond: Bond, current_lt_rate: float) -> float:
    """
    Compute approximate bond market price per $100 face given current LT rate.
    Higher current rates -> lower bond prices (and vice versa).
    Simplified: price ~ 100 × (coupon / current_rate)
    """
    if current_lt_rate <= 0:
        return 100.0
    return min(120.0, max(60.0, 100.0 * bond.coupon_rate / current_lt_rate))


def calculate_credit_rating(leverage: float) -> str:
    """
    Credit rating from leverage (Assets/Equity).
    Per Capsim guide: AAA at 1.0, drops 1 rating per ~0.5 leverage point.
    """
    if leverage <= 1.0: return "AAA"
    if leverage <= 1.5: return "AA"
    if leverage <= 2.0: return "A"
    if leverage <= 2.5: return "BBB"
    if leverage <= 3.0: return "BB"
    if leverage <= 3.5: return "B"
    if leverage <= 4.0: return "CCC"
    if leverage <= 4.5: return "CC"
    if leverage <= 5.0: return "C"
    if leverage <= 5.5: return "DDD"
    if leverage <= 6.0: return "DD"
    return "D"


def max_new_bond_capacity(company: Company) -> float:
    """How much more bond debt the company can take on."""
    plant = sum(plant_value(p) for p in company.products)
    cap = plant * MAX_BOND_DEBT_RATIO
    current_bonds = sum(b.face_value for b in company.bonds)
    return max(0.0, cap - current_bonds)


def issue_bond(company: Company, amount: float, prime_rate: float, year: int) -> Dict:
    """
    Issue a new bond. Returns dict with details.
    Limited by max bond capacity.
    """
    available = max_new_bond_capacity(company)
    amount = min(amount, available)
    if amount <= 0:
        return {"issued": 0, "net_proceeds": 0, "rate": 0, "fee": 0, "series": None}

    rate = long_term_rate(prime_rate, company.sp_rating) + 0.005  # +0.5% over LT rate base
    fee = amount * BOND_BROKERAGE_FEE
    net_proceeds = amount - fee

    series = f"{rate*100:.1f}S{year + BOND_TERM_YEARS}"
    new_bond = Bond(
        series=series,
        face_value=amount,
        coupon_rate=rate,
        year_due=year + BOND_TERM_YEARS,
        market_close=100.0,
        yield_to_maturity=rate,
    )
    company.bonds.append(new_bond)
    company.cash += net_proceeds
    return {
        "issued": amount,
        "net_proceeds": net_proceeds,
        "rate": rate,
        "fee": fee,
        "series": series,
    }


def retire_bond_early(company: Company, series: str) -> Dict:
    """
    Retire a bond before maturity. Pays face × market_price/100 + 1.5% fee.
    """
    bond = next((b for b in company.bonds if b.series == series), None)
    if bond is None:
        return {"retired": 0, "cash_out": 0, "fee": 0}

    market_price = bond.market_close / 100.0
    cash_paid = bond.face_value * market_price
    fee = bond.face_value * EARLY_RETIRE_FEE
    total_out = cash_paid + fee

    company.cash -= total_out
    company.bonds.remove(bond)

    return {
        "retired": bond.face_value,
        "cash_out": total_out,
        "fee": fee,
        "market_price": market_price,
    }


def retire_matured_bonds(company: Company, current_year: int) -> List[Dict]:
    """
    Retire bonds that have matured (year_due <= current_year).
    Pays face value out of cash (or converts to current debt if cash short).
    """
    results = []
    for bond in list(company.bonds):
        if bond.year_due <= current_year:
            company.cash -= bond.face_value
            company.bonds.remove(bond)
            results.append({"matured": bond.series, "amount": bond.face_value})
    return results


def total_bond_interest(company: Company) -> float:
    """Annual interest on all outstanding bonds."""
    return sum(b.face_value * b.coupon_rate for b in company.bonds)


def issue_stock(company: Company, amount: float, current_price: Optional[float] = None) -> Dict:
    """Issue new stock. Adds to common_stock + cash, dilutes shares.
    Rejects if amount <= $500K fee (would create negative net proceeds)."""
    if current_price is None:
        current_price = company.stock_price
    if current_price <= 0 or amount <= STOCK_ISSUE_FEE:
        return {"issued": 0, "shares": 0, "net": 0, "fee": 0, "rejected": True}
    fee = STOCK_ISSUE_FEE
    net = amount - fee
    new_shares = int(net / current_price)
    if new_shares <= 0:
        return {"issued": 0, "shares": 0, "net": 0, "fee": 0, "rejected": True}
    company.shares_outstanding += new_shares
    company.common_stock += net
    company.cash += net
    return {"issued": amount, "shares": new_shares, "net": net, "fee": fee}


def buyback_stock(company: Company, amount: float, current_price: Optional[float] = None) -> Dict:
    """Buy back shares at current market price. Reduces shares and equity."""
    if current_price is None:
        current_price = company.stock_price
    if current_price <= 0 or amount <= 0:
        return {"bought": 0, "shares": 0}
    shares = int(amount / current_price)
    company.shares_outstanding -= shares
    company.retained_earnings -= amount  # reduces equity
    company.cash -= amount
    return {"bought": amount, "shares": shares, "price": current_price}


def pay_dividend(company: Company, per_share: float) -> float:
    """Pay dividend per share. Returns total cash out."""
    total = per_share * company.shares_outstanding
    company.cash -= total
    company.retained_earnings -= total
    return total


def emergency_loan_if_needed(company: Company, prime_rate: float) -> float:
    """If cash < 0, take emergency loan at penalty rate.
    Reflects ONLY this round's draw — reset to 0 when not needed so the flag
    doesn't stick on the balance sheet/UI after the company recovers."""
    if company.cash >= 0:
        company.emergency_loan = 0
        return 0
    loan = -company.cash
    company.cash = 0
    company.current_debt += loan
    company.emergency_loan = loan
    return loan


def update_stock_price(company: Company) -> float:
    """
    Stock price update based on Book Value, EPS, Dividend.

    Re-calibrated to be less punishing on dividend cuts (real Capsim
    investors care more about EPS than dividend yield).

    Old: BV + 3×EPS + 5×Div (heavy dividend dependence)
    New: BV + 5×EPS + 2×Div (EPS-heavy, like real P/E investors)

    Andrews R0: BV $34.65 + 5×$9.80 + 2×$6.50 = 34.65 + 49 + 13 = $96.65 ≈ $95.38 ✓
    R2 with EPS dropped to $7.36 and div cut to $3:
      Old: 39.02 + 22.08 + 15 = $76.10 (over-punished)
      New: 39.02 + 36.80 + 6   = $81.82 (more realistic)
    """
    bv_per_share = (company.total_equity / company.shares_outstanding
                    if company.shares_outstanding > 0 else 0)
    eps = company.eps
    div = company.dividend_per_share
    new_price = bv_per_share + 5.0 * eps + 2.0 * div
    company.stock_price = max(1.0, new_price)
    company.market_cap = company.stock_price * company.shares_outstanding
    return company.stock_price


def compute_ratios(company: Company) -> Dict:
    """Compute key financial ratios."""
    sales = max(1, company.sales_last)
    assets = max(1, company.total_assets)
    equity = max(1, company.total_equity)

    ros = company.profit_last / sales
    asset_turnover = sales / assets
    roa = company.profit_last / assets
    leverage = assets / equity
    roe = company.profit_last / equity

    company.ros = ros
    company.asset_turnover = asset_turnover
    company.roa = roa
    company.leverage = leverage
    company.roe = roe
    company.sp_rating = calculate_credit_rating(leverage)
    return {
        "ROS": ros, "Asset_Turnover": asset_turnover, "ROA": roa,
        "Leverage": leverage, "ROE": roe, "S&P": company.sp_rating,
    }


def income_statement(company: Company, year: int, prime_rate: float,
                     hr_admin_cost: float = 0, tqm_spend: float = 0,
                     rd_cost: float = 0) -> Dict:
    """
    Compute Income Statement with proper cost reductions applied.

    Sales = sum(units_sold_last × price) × 1000  (units in thousands)
    Variable Costs (per unit) properly applies:
      - automation reduction via labor_cost_factor(automation, productivity_index)
      - HR productivity_index (better workers = less labor cost per unit)
      - TQM material_cost_reduction
      - TQM labor_cost_reduction
    Contribution Margin = Sales - Variable
    SGA = R&D + Promo + Sales Budget + Admin (after TQM admin reduction) + HR Admin
    EBIT = CM - Depreciation - SGA - Other (TQM round spend)
    """
    sales = sum(p.units_sold_last * p.price for p in company.products) * 1000

    # Pull HR + TQM effects
    pi = company.hr.productivity_index
    tqm_mat = company.tqm.material_cost_reduction      # negative = reduction
    tqm_lab = company.tqm.labor_cost_reduction
    tqm_adm = company.tqm.admin_cost_reduction

    # Variable costs — labor_cost in seed is ALREADY post-automation (from Inquirer).
    # Apply HR productivity_index, TQM reductions, AND 2nd-shift labor premium (1.5×).
    # Use units_PRODUCED (not sold) — Capsim charges variable cost on production; unsold goes to inventory.
    from sim.engines.production import SECOND_SHIFT_LABOR_MULTIPLIER
    var_labor = 0.0
    var_material = 0.0
    for p in company.products:
        # Base effective labor (1st shift): post-automation × HR × TQM
        base_labor = p.labor_cost / max(0.5, pi) * (1 + tqm_lab)
        prod_units = max(p.units_produced_last, p.units_sold_last)
        # Split into 1st-shift (regular rate) and 2nd-shift (1.5× premium)
        first_shift_units = min(prod_units, p.capacity_first_shift)
        second_shift_units = max(0, prod_units - p.capacity_first_shift)
        labor_per_product = (first_shift_units * base_labor
                             + second_shift_units * base_labor * SECOND_SHIFT_LABOR_MULTIPLIER)
        var_labor += labor_per_product * 1000
        # Material has no shift premium
        effective_material = p.material_cost * (1 + tqm_mat)
        var_material += effective_material * prod_units * 1000

    # Inventory carry: avg of (start, end) × 12% × unit cost
    inv_carry = sum(inventory_carry_cost(p, p.inventory) for p in company.products)
    var_total = var_labor + var_material + inv_carry
    contribution = sales - var_total

    depreciation = sum(annual_depreciation(p) for p in company.products)
    promo_total = sum(p.promo_budget for p in company.products)
    sales_total = sum(p.sales_budget for p in company.products)
    admin_base = sales * 0.015  # 1.5% of sales
    admin = admin_base * (1 + tqm_adm)  # TQM admin reduction
    sga = rd_cost + promo_total + sales_total + admin + hr_admin_cost
    other = tqm_spend

    ebit = contribution - depreciation - sga - other
    st_interest = company.current_debt * short_term_rate(prime_rate)
    lt_interest = total_bond_interest(company)
    pretax = ebit - st_interest - lt_interest
    taxes = max(0, pretax * TAX_RATE)
    after_tax = pretax - taxes
    profit_sharing = max(0, after_tax * PROFIT_SHARING_RATE)
    net_profit = after_tax - profit_sharing

    company.sales_last = sales
    company.ebit_last = ebit
    company.profit_last = net_profit
    company.cumulative_profit += net_profit
    company.contribution_margin_last = contribution
    company.sga_last = sga
    company.eps = net_profit / company.shares_outstanding if company.shares_outstanding > 0 else 0

    return {
        "sales": sales,
        "variable_labor": var_labor,
        "variable_material": var_material,
        "inventory_carry": inv_carry,
        "variable_total": var_total,
        "contribution_margin": contribution,
        "depreciation": depreciation,
        "promo": promo_total,
        "sales_budget": sales_total,
        "admin": admin,
        "hr_admin": hr_admin_cost,
        "sga": sga,
        "tqm": tqm_spend,
        "ebit": ebit,
        "short_term_interest": st_interest,
        "long_term_interest": lt_interest,
        "pretax_income": pretax,
        "taxes": taxes,
        "profit_sharing": profit_sharing,
        "net_profit": net_profit,
    }


def project_next_round_pl(state, company: Company, pending) -> Dict:
    """
    Estimate next round's P&L based on pending decisions (BEFORE advance_round).

    Used by Finance tab's Projected Cash Flow Summary to reflect HR/TQM/Marketing/
    R&D/Price changes that user just adjusted — not stale profit_last.

    pending: RoundDecision with .products, .hr, .tqm, .finance

    Returns dict with sales/variable/sga/profit/cash_from_ops estimates.
    """
    from sim.engines.production import SECOND_SHIFT_LABOR_MULTIPLIER, annual_depreciation
    from sim.engines.hr import productivity_index, employees_needed, recruiting_cost, training_cost, turnover_rate, BASE_TURNOVER
    from sim.engines.tqm import TQM_IMPACTS, TQM_FULL_EFFECT_CUMULATIVE, s_curve_factor
    from sim.engines.rd import rd_distance, rd_project_cost

    # === 1. PROJECTED HR (with new pending HR decision) ===
    new_pi = productivity_index(pending.hr.recruit_spend, pending.hr.training_hours)
    new_turnover = turnover_rate(pending.hr.training_hours)

    # Build pseudo-company with pending production_schedule to compute needed employees
    total_prod = sum((pd.production_schedule or 0) for pd in pending.products)
    needed_emp = max(50, int(total_prod * 0.144))
    cur_emp = company.hr.workforce_complement
    separated = int(cur_emp * new_turnover)
    new_hires = max(0, needed_emp - (cur_emp - separated))
    rec_cost = recruiting_cost(new_hires, pending.hr.recruit_spend)
    train_cost = training_cost(needed_emp, pending.hr.training_hours)
    hr_admin_total = rec_cost + train_cost

    # === 2. PROJECTED TQM (cumulative + this round's pending spend) ===
    proj_tqm_cum = dict(company.tqm.cumulative_spend)
    tqm_round_spend = 0.0
    for name, amt in (pending.tqm.initiatives or {}).items():
        if name not in TQM_IMPACTS:
            continue
        amt_capped = max(0, min(amt, 2_000_000))
        already = proj_tqm_cum.get(name, 0)
        amt_capped = min(amt_capped, max(0, TQM_FULL_EFFECT_CUMULATIVE - already))
        proj_tqm_cum[name] = already + amt_capped
        tqm_round_spend += amt_capped

    mat = lab = adm = 0.0
    for name, impacts in TQM_IMPACTS.items():
        cum = proj_tqm_cum.get(name, 0)
        if cum <= 0:
            continue
        f = s_curve_factor(cum)
        mat += impacts["material"] * f
        lab += impacts["labor"] * f
        adm += impacts["admin"] * f
    proj_tqm_mat = max(-0.118, mat)
    proj_tqm_lab = max(-0.14, lab)
    proj_tqm_adm = max(-0.60, adm)

    # === 3. PROJECTED SALES (from pending forecast or units_sold_last × growth) ===
    proj_sales = 0.0
    proj_var_labor = 0.0
    proj_var_material = 0.0
    for pd in pending.products:
        prod = next(p for p in company.products if p.name == pd.product_name)
        # Use forecast (000s) if set, else units_sold_last × (1+seg_growth)
        seg = next(s for s in state.segments if s.name == prod.primary_segment)
        forecast_units = pd.forecast or int(prod.units_sold_last * (1 + seg.growth_rate))
        price = pd.price if pd.price is not None else prod.price
        proj_sales += forecast_units * price * 1000

        # Variable costs: labor with NEW HR PI + NEW TQM lab reduction
        # Production = production_schedule (build to spec; unsold goes to inventory but still cost it)
        prod_units = pd.production_schedule or forecast_units
        base_labor = prod.labor_cost / max(0.5, new_pi) * (1 + proj_tqm_lab)
        # NEW automation reduces labor (already baked into prod.labor_cost; auto upgrade applies post-round)
        cap = prod.capacity_first_shift + (pd.capacity_change or 0)
        first_shift = min(prod_units, max(1, cap))
        second_shift = max(0, prod_units - cap)
        proj_var_labor += (first_shift * base_labor + second_shift * base_labor * SECOND_SHIFT_LABOR_MULTIPLIER) * 1000
        # Material: NEW TQM mat reduction
        eff_mat = prod.material_cost * (1 + proj_tqm_mat)
        proj_var_material += eff_mat * prod_units * 1000

    # === 4. R&D COST (from pending revisions) ===
    proj_rd_cost = 0.0
    for pd in pending.products:
        if pd.new_pfmn is not None or pd.new_size is not None or pd.new_mtbf is not None:
            prod = next(p for p in company.products if p.name == pd.product_name)
            np_pfmn = pd.new_pfmn if pd.new_pfmn is not None else prod.pfmn
            np_size = pd.new_size if pd.new_size is not None else prod.size
            np_mtbf = pd.new_mtbf if pd.new_mtbf is not None else prod.mtbf
            proj_rd_cost += rd_project_cost(prod, np_pfmn, np_size, np_mtbf)

    # === 5. SG&A — uses NEW HR cost, NEW TQM spend, NEW marketing ===
    promo_total = sum((pd.promo_budget or 0) for pd in pending.products)
    sales_total = sum((pd.sales_budget or 0) for pd in pending.products)
    depreciation = sum(annual_depreciation(p) for p in company.products)
    admin = proj_sales * 0.015 * (1 + proj_tqm_adm)
    sga = proj_rd_cost + promo_total + sales_total + admin + hr_admin_total

    contribution = proj_sales - proj_var_labor - proj_var_material
    ebit = contribution - depreciation - sga - tqm_round_spend
    st_int = company.current_debt * short_term_rate(state.prime_interest_rate)
    lt_int = total_bond_interest(company)
    pretax = ebit - st_int - lt_int
    taxes = max(0, pretax * TAX_RATE)
    after_tax = pretax - taxes
    profit_sharing = max(0, after_tax * PROFIT_SHARING_RATE)
    net_profit = after_tax - profit_sharing

    return {
        "sales": proj_sales,
        "variable_labor": proj_var_labor,
        "variable_material": proj_var_material,
        "contribution": contribution,
        "depreciation": depreciation,
        "rd_cost": proj_rd_cost,
        "promo": promo_total,
        "sales_budget": sales_total,
        "admin": admin,
        "hr_admin": hr_admin_total,
        "tqm_spend": tqm_round_spend,
        "sga": sga,
        "ebit": ebit,
        "interest": st_int + lt_int,
        "taxes": taxes,
        "net_profit": net_profit,
        "cash_from_operations": net_profit + depreciation,
        # Debug breakdown for tooltip
        "new_pi": new_pi,
        "new_hires": new_hires,
        "tqm_mat_pct": proj_tqm_mat * 100,
        "tqm_lab_pct": proj_tqm_lab * 100,
        "tqm_adm_pct": proj_tqm_adm * 100,
    }


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    print("=== Financial summary R0 ===\n")
    for c in state.companies:
        ratios = compute_ratios(c)
        max_bond = max_new_bond_capacity(c)
        print(f"{c.name}:")
        print(f"  Sales ${c.sales_last/1e6:.1f}M  Profit ${c.profit_last/1e6:.1f}M  ROS {ratios['ROS']*100:.1f}%")
        print(f"  Assets ${c.total_assets/1e6:.1f}M  Equity ${c.total_equity/1e6:.1f}M  Lev {ratios['Leverage']:.2f}  Rating {ratios['S&P']}")
        print(f"  Bonds outstanding ${sum(b.face_value for b in c.bonds)/1e6:.1f}M, max new ${max_bond/1e6:.1f}M")
        print(f"  Stock ${c.stock_price:.2f}  MarketCap ${c.market_cap/1e6:.0f}M  ROE {ratios['ROE']*100:.1f}%\n")
