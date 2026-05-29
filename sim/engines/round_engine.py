"""
Round Advancement Engine — orchestrates one round of Comp-XM simulation.

Sequence per round:
  1. Apply Andrews decisions (R&D, Marketing, Production, Finance, HR, TQM)
  2. Generate AI decisions for Baldwin, Chester, Digby
  3. Apply AI decisions
  4. Advance the year:
     a. Segments drift
     b. Industry demand grows
     c. Products age +1 (or completed R&D revisions apply)
     d. Plant depreciates
     e. Awareness/Accessibility decay (handled in marketing.update_*)
  5. Compute production cost (per product, with HR productivity + TQM)
  6. Allocate demand & ship (with stockout reallocation)
  7. Compute Income Statement / Balance Sheet / Cash Flow
  8. Update stock price, credit rating, ratios
  9. Compute BSC for the round
  10. Snapshot state into history
"""
from __future__ import annotations
from typing import Optional, List, Dict
from copy import deepcopy
from sim.data_models import (
    GameState, RoundDecision, Company, Product, FinanceDecision,
    HRDecision, TQMDecision, BSCScore,
)
from sim.engines.demand import drift_segments, grow_industry_demand, allocate_demand, apply_stockouts
from sim.engines.customer_score import net_score
from sim.engines.production import (
    schedule_production, capacity_purchase_cost, automation_upgrade_cost,
    capacity_sell_value, plant_value, annual_depreciation, labor_cost_factor,
)
from sim.engines.marketing import update_awareness, update_accessibility
from sim.engines.rd import apply_revise, end_of_year_apply_completed_projects, advance_age_one_year, rd_project_cost
from sim.engines.finance import (
    income_statement, compute_ratios, update_stock_price, retire_matured_bonds,
    issue_bond, retire_bond_early, issue_stock, buyback_stock, pay_dividend,
    emergency_loan_if_needed, short_term_rate,
)
from sim.engines.hr import update_hr, labor_cost_adjustment
from sim.engines.tqm import update_tqm
from sim.ai_competitors import baldwin_decisions, chester_decisions, digby_decisions
from sim.engines.bsc import compute_round_bsc


def apply_company_decisions(company: Company, decisions: RoundDecision,
                              state: GameState, all_companies: List[Company]) -> Dict:
    """
    Apply one company's decisions for the round. Returns spending summary.
    """
    rd_total_cost = 0.0
    automation_total_cost = 0.0
    capacity_buy_cost = 0.0
    capacity_sell_proceeds = 0.0
    round_start = f"{state.year + 1}-01-01"
    rd_cycle_reduction = company.tqm.rd_cycle_time_reduction

    # Per-product decisions
    for pdec in decisions.products:
        p = next((p for p in company.products if p.name == pdec.product_name), None)
        if not p:
            continue

        # R&D revise — fire if ANY field changed (pfmn / size / mtbf).
        # Fill missing fields with current product values so a partial change
        # (e.g., just pfmn) still applies the revise. Previously, leaving MTBF
        # at default (= current) made new_mtbf=None which skipped the entire
        # revise — pfmn/size changes were silently discarded.
        if (pdec.new_pfmn is not None or pdec.new_size is not None
                or pdec.new_mtbf is not None):
            tgt_pfmn = pdec.new_pfmn if pdec.new_pfmn is not None else p.pfmn
            tgt_size = pdec.new_size if pdec.new_size is not None else p.size
            tgt_mtbf = pdec.new_mtbf if pdec.new_mtbf is not None else p.mtbf
            cost = rd_project_cost(p, tgt_pfmn, tgt_size, tgt_mtbf)
            rd_total_cost += cost
            apply_revise(p, tgt_pfmn, tgt_size, tgt_mtbf,
                         round_start_date=round_start,
                         rd_cycle_reduction=-rd_cycle_reduction)  # TQM reduction is negative

        # Pricing
        if pdec.price is not None:
            p.price = pdec.price

        # Marketing — ALWAYS decay awareness (call with $0 if no decision)
        # so awareness doesn't stay frozen at prior value when user submits blank
        update_awareness(p, pdec.promo_budget if pdec.promo_budget is not None else 0)

        # Track sales_budget on product (used later for accessibility update in advance_round)
        if pdec.sales_budget is not None:
            p.sales_budget = pdec.sales_budget

        # Store raw production_schedule for now — RE-CLAMP after cap_change
        if pdec.production_schedule is not None:
            p.production_schedule = max(0, pdec.production_schedule)

        # Sales Forecast (stored for BSC accuracy scoring next round)
        if pdec.forecast is not None:
            p.forecast_last = max(0, pdec.forecast)

        # Capacity changes — clamp oversell to available capacity
        if pdec.capacity_change != 0:
            if pdec.capacity_change > 0:
                cost = capacity_purchase_cost(pdec.capacity_change, p.automation)
                capacity_buy_cost += cost
                p.capacity_first_shift += pdec.capacity_change
            else:
                # Clamp sell to not exceed current capacity
                sell_units = min(-pdec.capacity_change, p.capacity_first_shift)
                proceeds = capacity_sell_value(sell_units, p.automation)
                capacity_sell_proceeds += proceeds
                # Reduce accumulated_depreciation proportionally to capacity sold
                # (sold plant takes its share of accum_dep with it)
                if p.capacity_first_shift > 0:
                    sold_fraction = sell_units / p.capacity_first_shift
                    dep_reduction = company.accumulated_depreciation * sold_fraction * (
                        plant_value(p) / max(1, sum(plant_value(pp) for pp in company.products))
                    )
                    company.accumulated_depreciation = max(0, company.accumulated_depreciation - dep_reduction)
                p.capacity_first_shift = max(0, p.capacity_first_shift - sell_units)

        # Automation upgrade — RESCALE labor_cost so new automation actually reduces labor
        # (seed labor_cost is already post-automation for current level; need to rescale to new level)
        if pdec.new_automation is not None and pdec.new_automation > p.automation:
            cost = automation_upgrade_cost(p.capacity_first_shift, p.automation, pdec.new_automation)
            automation_total_cost += cost
            from sim.engines.production import labor_cost_factor as _lcf
            old_factor = _lcf(p.automation)
            new_factor = _lcf(pdec.new_automation)
            if old_factor > 0:
                # Scale labor proportionally to factor reduction
                p.labor_cost = round(p.labor_cost * new_factor / old_factor, 2)
            p.automation = pdec.new_automation

        # RE-CLAMP production_schedule against EFFECTIVE capacity (after cap_change)
        # This ensures user can't produce more than 2× post-sell capacity
        from sim.engines.production import MAX_UTILIZATION
        max_units = int(p.capacity_first_shift * MAX_UTILIZATION)
        p.production_schedule = max(0, min(p.production_schedule, max_units))

    # NOTE: Accessibility update is now done ONCE in advance_round() after all companies
    # apply decisions (avoids 4x decay bug). Per-company sales_budget already set on products
    # via the loop above.

    # HR
    hr_result = update_hr(company, decisions.hr.recruit_spend, decisions.hr.training_hours)

    # TQM
    tqm_result = update_tqm(company, decisions.tqm.initiatives)

    # Finance: bonds & stock first
    bond_issue_proceeds = 0.0
    for b in list(company.bonds):
        if b.series in decisions.finance.retire_bond_early:
            ret = retire_bond_early(company, b.series)
    if decisions.finance.issue_bond > 0:
        result = issue_bond(company, decisions.finance.issue_bond,
                             state.prime_interest_rate, state.year + 1)
        bond_issue_proceeds = result["net_proceeds"]
    if decisions.finance.issue_stock > 0:
        issue_stock(company, decisions.finance.issue_stock)
    if decisions.finance.buyback_stock > 0:
        buyback_stock(company, decisions.finance.buyback_stock)

    # Cash out for capex ONLY (automation + capacity).
    # R&D is OPERATING expense — handled via income_statement SGA → reduces profit
    # which then reduces cash via "cash += profit". Don't double-deduct here.
    company.cash -= automation_total_cost + capacity_buy_cost
    company.cash += capacity_sell_proceeds

    return {
        "rd_cost": rd_total_cost,
        "automation_cost": automation_total_cost,
        "capacity_buy": capacity_buy_cost,
        "capacity_sell": capacity_sell_proceeds,
        "bond_issued": bond_issue_proceeds,
        "hr_admin": hr_result["total_hr_admin"],
        "tqm_spend": tqm_result["round_spend"],
    }


def produce_and_sell(state: GameState) -> Dict[str, Dict]:
    """
    Run production + demand allocation + sales for the round.
    Updates products with units_produced_last, units_sold_last.
    Returns dict {company_name: production_summary}.
    """
    # Allocate demand
    alloc = allocate_demand(state, state.industry_unit_demand)
    units_sold, total_demand = apply_stockouts(state, alloc)

    company_summary = {}
    for c in state.companies:
        company_units_sold = 0
        company_units_produced = 0
        company_revenue = 0.0
        for p in c.products:
            sold = units_sold.get(p.name, 0)
            produced = min(p.production_schedule, p.inventory + p.production_schedule)
            p.units_sold_last = sold
            p.units_produced_last = p.production_schedule
            # End-of-round inventory
            ending_inv = max(0, p.inventory + p.production_schedule - sold)
            p.inventory = ending_inv
            # Revenue (units thousands × price × 1000 = $)
            p.revenue_last = sold * p.price * 1000
            company_units_sold += sold
            company_units_produced += p.production_schedule
            company_revenue += p.revenue_last
        company_summary[c.name] = {
            "units_sold": company_units_sold,
            "units_produced": company_units_produced,
            "revenue": company_revenue,
        }
    return company_summary


def year_end_advance(state: GameState) -> None:
    """
    End-of-year transitions:
      - Apply completed R&D projects (position/MTBF/age update)
      - For products without revise, age +1 year
      - Retire matured bonds
      - Drift segments + grow demand for NEXT round
    """
    year_start = f"{state.year + 1}-01-01"
    year_end = f"{state.year + 1}-12-31"
    for c in state.companies:
        for p in c.products:
            completed = end_of_year_apply_completed_projects(p, year_end, year_start)
            if not completed:
                advance_age_one_year(p)
        # Retire matured bonds
        retire_matured_bonds(c, state.year + 1)


def advance_round(state: GameState, andrews_decisions: RoundDecision,
                   prev_state: Optional[GameState] = None) -> Dict:
    """
    Run one full round: apply decisions, simulate, compute reports.
    Returns dict with round results + BSC.
    """
    summary = {
        "round_num": state.round_num + 1,
        "year_from": state.year,
        "year_to": state.year + 1,
        "decisions_applied": {},
        "production_summary": {},
        "financials": {},
        "bsc": None,
    }

    # 1. Apply Andrews decisions
    andrews = state.get_company("Andrews")
    spend_andrews = apply_company_decisions(andrews, andrews_decisions, state, state.companies)
    summary["decisions_applied"]["Andrews"] = spend_andrews

    # Track each company's decision so the financials step can honor its own
    # finance choices (dividend, AR/AP lag, current-debt borrow) — not just Andrews'.
    decisions_by_company = {"Andrews": andrews_decisions}

    # 2. Generate + apply AI decisions
    for ai_name, gen_fn in [("Baldwin", baldwin_decisions),
                              ("Chester", chester_decisions),
                              ("Digby", digby_decisions)]:
        ai_decs = gen_fn(state)
        decisions_by_company[ai_name] = ai_decs
        spend = apply_company_decisions(state.get_company(ai_name), ai_decs, state, state.companies)
        summary["decisions_applied"][ai_name] = spend

    # 2.5 Accessibility update — ONCE after all 4 companies set their sales budgets
    # (was being called 4x inside apply_company_decisions causing 4x decay)
    for seg in state.segments:
        sales_per_product: Dict[str, float] = {}
        for c2 in state.companies:
            for pp in c2.products:
                if pp.primary_segment == seg.name:
                    sales_per_product[pp.name] = pp.sales_budget
        update_accessibility(state.companies, seg.name, sales_per_product)

    # 2.7 Advance market + products to END-OF-YEAR *before* scoring/selling.
    # CAPSIM TIMING FIX (was off-by-one): the December customer survey is scored
    # against the year's ENDING segment positions, and a product revised this year
    # sells at its NEW position for the rest of the year. So we must:
    #   (a) grow industry demand to this year's level,
    #   (b) drift segment centers to this year's end position,
    #   (c) finalize completed R&D revisions (position/MTBF/age-halve) and age the rest,
    # ALL before produce_and_sell. Previously these ran AFTER the sale, so revising
    # toward a round's ideal spot only paid off the FOLLOWING round (contradicting the
    # cheatsheet strategy) and segments were scored at last year's location.
    state.industry_unit_demand = grow_industry_demand(state)
    drift_segments(state)
    _ys = f"{state.year + 1}-01-01"
    _ye = f"{state.year + 1}-12-31"
    for _c in state.companies:
        for _p in _c.products:
            if not end_of_year_apply_completed_projects(_p, _ye, _ys):
                advance_age_one_year(_p)
        retire_matured_bonds(_c, state.year + 1)

    # 3. Produce + sell (now scored at end-of-year segment + product positions)
    prod_summary = produce_and_sell(state)
    summary["production_summary"] = prod_summary

    # 3.5 Update industry_unit_sold by segment for the Inquirer (FIX: was stale at R0 forever)
    new_industry_sold = {s.name: 0 for s in state.segments}
    for c in state.companies:
        for p in c.products:
            new_industry_sold[p.primary_segment] = new_industry_sold.get(p.primary_segment, 0) + p.units_sold_last
    state.industry_unit_sold = new_industry_sold

    # 4. Calculate financials per company
    for c in state.companies:
        # HR admin cost
        hr_admin = c.hr.total_hr_admin_cost
        # TQM spend this round
        tqm_round_spend = sum(c.tqm.spend_this_round.values())
        # RD + automation + capacity already deducted from cash in apply_company_decisions
        # but should also appear in income statement as SGA/Other
        # R&D cost (recompute from this round's spend)
        rd_spent = summary["decisions_applied"].get(c.name, {}).get("rd_cost", 0)
        is_dict = income_statement(c, state.year + 1, state.prime_interest_rate,
                                   hr_admin_cost=hr_admin, tqm_spend=tqm_round_spend,
                                   rd_cost=rd_spent)
        # Cash flow: cash already updated by various functions
        # Pay dividend — honor each company's own decision (AI sets it in ai_competitors
        # from prior-year profit, like a real board declaring before results are known).
        dec_fin = decisions_by_company[c.name].finance
        div = dec_fin.dividend_per_share
        c.dividend_per_share = round(div, 2)
        if div > 0:
            pay_dividend(c, div)

        # === Cash Flow from Operations (GAAP) ===
        # = NetProfit + Depreciation - ΔAR - ΔInv + ΔAP
        depreciation = sum(annual_depreciation(p) for p in c.products)

        # Snapshot pre-update working capital
        old_ar = c.accounts_receivable
        old_ap = c.accounts_payable
        old_inv = c.inventory_value

        # Compute new working capital (labor in seed is post-automation — no factor)
        new_inv = sum(
            p.inventory * (p.material_cost + p.labor_cost / max(0.5, c.hr.productivity_index)) * 1000
            for p in c.products
        )
        # AR/AP lag — each company's own policy (AI defaults to 30 days)
        ar_lag = dec_fin.accounts_receivable_lag
        ap_lag = dec_fin.accounts_payable_lag
        new_ar = c.sales_last * ar_lag / 365
        new_ap = (sum(p.material_cost * p.units_produced_last for p in c.products) * 1000) * ap_lag / 365

        # Apply cash flow with working capital deltas
        delta_ar = new_ar - old_ar
        delta_ap = new_ap - old_ap
        delta_inv = new_inv - old_inv
        c.cash += c.profit_last + depreciation - delta_ar - delta_inv + delta_ap

        # === Repay current debt (Capsim: short-term debt due annually) ===
        # Then re-borrow if user requested new current_debt_borrow
        repay = c.current_debt
        c.cash -= repay  # pay off prior current debt
        new_borrow = dec_fin.current_debt_borrow  # honor each company's borrow decision
        c.current_debt = new_borrow
        c.cash += new_borrow

        # Emergency loan if cash went negative (adds to current_debt for next year)
        em_loan = emergency_loan_if_needed(c, state.prime_interest_rate)

        # Commit new BS items
        c.accumulated_depreciation += depreciation
        c.inventory_value = new_inv
        c.accounts_receivable = new_ar
        c.accounts_payable = new_ap
        c.retained_earnings += c.profit_last  # less dividends (already paid above)

        # Update plant value to actual current
        c.plant_value = sum(plant_value(p) for p in c.products)

        # Update ratios + stock price + rating
        compute_ratios(c)
        update_stock_price(c)

        summary["financials"][c.name] = is_dict

    # 5. (Market advance, R&D completion, aging, and bond maturity already happened
    #     in step 2.7 — before the sale — per the Capsim timing fix.)
    state.round_num += 1
    state.year += 1

    # 7. BSC for this round
    bsc = compute_round_bsc(state, "Andrews", prev_state=prev_state)
    summary["bsc"] = bsc.model_dump()

    # 8. Snapshot history
    state.history.append({
        "round": state.round_num,
        "year": state.year,
        "andrews_profit": andrews.profit_last,
        "andrews_stock": andrews.stock_price,
        "andrews_cash": andrews.cash,
        "andrews_marketcap": andrews.market_cap,
        "andrews_bsc": bsc.total,
    })

    return summary


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    from sim.data_models import RoundDecision, ProductDecision, FinanceDecision, HRDecision, TQMDecision

    state = build_r0_state()
    print("=== R1 Test: Andrews makes sensible decisions ===")

    # Andrews R1 decisions:
    # - Revise Attic (critical: age 5.1)
    # - Hold Axe (age 2.2, good)
    # - Revise Art + Ant to track segment drift
    # - Production: aim 150% utilization
    # - Retire 13.5S2027 bond
    # - HR: $2500 + 40hr
    # - TQM: $9M conservative
    andrews_dec = RoundDecision(
        round_num=1,
        products=[
            ProductDecision(
                product_name="Attic",
                new_pfmn=6.2, new_size=13.8, new_mtbf=20000,
                price=24.00, promo_budget=1500000, sales_budget=1000000,
                production_schedule=1700,
            ),
            ProductDecision(
                product_name="Axe",
                price=31.00, promo_budget=1500000, sales_budget=1500000,
                production_schedule=2000,
            ),
            ProductDecision(
                product_name="Art",
                new_pfmn=10.5, new_size=7.2, new_mtbf=24000,
                price=38.00, promo_budget=1500000, sales_budget=1500000,
                production_schedule=1100,
            ),
            ProductDecision(
                product_name="Ant",
                new_pfmn=12.8, new_size=9.5, new_mtbf=26000,
                price=40.00, promo_budget=1500000, sales_budget=1500000,
                production_schedule=1100,
            ),
        ],
        finance=FinanceDecision(
            retire_bond_early=["13.5S2027"],
            dividend_per_share=6.00,
        ),
        hr=HRDecision(recruit_spend=2500, training_hours=40),
        tqm=TQMDecision(initiatives={
            "QFD Effort": 1_500_000, "CCE/6 Sigma": 1_500_000,
            "Vendor/JIT": 1_500_000, "CPI Systems": 1_500_000,
            "Concurrent Engineering": 1_500_000, "GEMI TQEM": 1_500_000,
        }),
    )

    result = advance_round(state, andrews_dec)
    print(f"\nRound {result['round_num']} ({result['year_from']}->{result['year_to']}) complete\n")
    print("Decisions cost summary:")
    for cname, costs in result["decisions_applied"].items():
        print(f"  {cname}: RD ${costs['rd_cost']/1e6:.1f}M, Auto ${costs['automation_cost']/1e6:.1f}M, "
              f"HR ${costs['hr_admin']/1e6:.2f}M, TQM ${costs['tqm_spend']/1e6:.1f}M")

    print("\nProduction summary:")
    for cname, prod in result["production_summary"].items():
        print(f"  {cname}: produced {prod['units_produced']}, sold {prod['units_sold']}, revenue ${prod['revenue']/1e6:.1f}M")

    print("\nAndrews R1 financials:")
    andrews = state.get_company("Andrews")
    print(f"  Cash: ${andrews.cash/1e6:.1f}M")
    print(f"  Profit: ${andrews.profit_last/1e6:.1f}M (R0 was $20.1M)")
    print(f"  Stock: ${andrews.stock_price:.2f} (R0 was $95.38)")
    print(f"  ROS: {andrews.ros*100:.1f}%, ROE: {andrews.roe*100:.1f}%, Leverage: {andrews.leverage:.2f}")
    print(f"  Rating: {andrews.sp_rating}")

    print(f"\nR1 BSC Score: {result['bsc']['total']:.1f}")
    print(f"  Financial: {result['bsc']['financial']:.1f}")
    print(f"  Internal Bus: {result['bsc']['internal_business']:.1f}")
    print(f"  Customer: {result['bsc']['customer']:.1f}")
    print(f"  Learning&Growth: {result['bsc']['learning_growth']:.1f}")
