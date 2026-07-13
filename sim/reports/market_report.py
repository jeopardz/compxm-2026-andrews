"""
BizSim market report generator.

Produces:
  - Front Page (financial summary across 4 companies)
  - Stocks & Bonds page
  - Financial Summary (IS / BS / CF survey table)
  - Production Analysis
  - 4× Segment Analysis pages (Thrift/Core/Nano/Elite)
  - Market Share Report
  - Perceptual Map data
  - HR/TQM Summary
  - Per-company Annual Reports

The market report shows only the current round's data (no history), while
annual reports for all four companies are included.
"""
from __future__ import annotations
from typing import Dict, List
from sim.data_models import GameState, Company, Product, Segment
from sim.engines.customer_score import net_score, in_rough_cut, score_breakdown
from sim.engines.production import inventory_carry_cost, annual_depreciation, plant_value


def front_page(state: GameState) -> Dict:
    """Selected Financial Statistics for all 4 companies."""
    data = {}
    for c in state.companies:
        data[c.name] = {
            "ROS": f"{c.ros*100:.1f}%",
            "Asset_Turnover": f"{c.asset_turnover:.2f}",
            "ROA": f"{c.roa*100:.1f}%",
            "Leverage": f"{c.leverage:.2f}",
            "ROE": f"{c.roe*100:.1f}%",
            "Emergency_Loan": f"${c.emergency_loan/1e6:.1f}M" if c.emergency_loan > 0 else "$0",
            "Sales": f"${c.sales_last/1e6:.1f}M",
            "EBIT": f"${c.ebit_last/1e6:.1f}M",
            "Profits": f"${c.profit_last/1e6:.1f}M",
            "Cumulative_Profit": f"${c.cumulative_profit/1e6:.1f}M",
            "SGA_Sales": f"{c.sga_last / max(1,c.sales_last)*100:.1f}%",
            "Contrib_Margin": f"{c.contribution_margin_last / max(1,c.sales_last)*100:.1f}%",
        }
    return {"title": f"Round {state.round_num} | Dec 31 {state.year}", "data": data}


def stocks_bonds_page(state: GameState) -> Dict:
    """Stock & Bond market summary."""
    stocks = []
    for c in state.companies:
        stocks.append({
            "Company": c.name,
            "Close$": f"${c.stock_price:.2f}",
            "Shares": f"{c.shares_outstanding:,}",
            "MarketCap_M": f"${c.market_cap/1e6:.0f}M",
            "BookValuePerShare": f"${c.book_value_per_share:.2f}",
            "EPS": f"${c.eps:.2f}",
            "Dividend": f"${c.dividend_per_share:.2f}",
            "Yield": f"{c.dividend_per_share/max(0.01,c.stock_price)*100:.1f}%" if c.stock_price > 0 else "0%",
            "PE": f"{c.stock_price/max(0.01,c.eps):.1f}" if c.eps > 0 else "N/A",
        })
    bonds = []
    for c in state.companies:
        for b in c.bonds:
            bonds.append({
                "Company": c.name,
                "Series": b.series,
                "Face_M": f"${b.face_value/1e6:.1f}M",
                "Yield": f"{b.yield_to_maturity*100:.1f}%",
                "Close": f"${b.market_close:.2f}",
                "Rating": c.sp_rating,
            })
    return {
        "stocks": stocks,
        "bonds": bonds,
        "next_prime_rate": f"{state.prime_interest_rate*100:.1f}%",
    }


def financial_summary_table(state: GameState) -> Dict:
    """IS / BS / CF survey table comparing 4 companies."""
    cols = ["Apex", "Borealis", "Crestline", "Dynamo"]
    data = {}
    for c in state.companies:
        data[c.name] = {
            # Income Statement
            "Sales": c.sales_last,
            "Variable_Costs": c.sales_last - c.contribution_margin_last,
            "Contribution_Margin": c.contribution_margin_last,
            "SGA": c.sga_last,
            "EBIT": c.ebit_last,
            "Net_Profit": c.profit_last,
            # Balance Sheet
            "Cash": c.cash,
            "AR": c.accounts_receivable,
            "Inventory": c.inventory_value,
            "Plant_Net": c.plant_value - c.accumulated_depreciation,
            "Total_Assets": c.total_assets,
            "AP": c.accounts_payable,
            "Current_Debt": c.current_debt,
            "LT_Debt": sum(b.face_value for b in c.bonds),
            "Common_Stock": c.common_stock,
            "Retained_Earnings": c.retained_earnings,
            "Total_Equity": c.total_equity,
        }
    return data


def production_analysis(state: GameState) -> List[Dict]:
    """Production info for ALL products across companies."""
    rows = []
    for c in state.companies:
        for p in c.products:
            cap = p.capacity_first_shift
            util = (p.units_produced_last / cap * 100) if cap > 0 else 0
            rows.append({
                "Company": c.name,
                "Name": p.name,
                "Segment": p.primary_segment,
                "Units_Sold": p.units_sold_last,
                "Inventory": p.inventory,
                "Revision_Date": p.revision_date,
                "Age": p.age,
                "MTBF": p.mtbf,
                "Pfmn": p.pfmn,
                "Size": p.size,
                "Price": p.price,
                "Material_Cost": p.material_cost,
                "Labor_Cost": p.labor_cost,
                "Automation": p.automation,
                "Capacity_Next": cap,
                "Utilization_Pct": util,
            })
    return rows


def segment_analysis(state: GameState, segment_name: str) -> Dict:
    """Full segment analysis page for one segment."""
    seg = state.get_segment(segment_name)
    total_demand = state.industry_unit_demand.get(segment_name, 0)
    actual_sold = state.industry_unit_sold.get(segment_name, 0)

    # === Compute per-segment SCORE shares (for market share %) ===
    # Each product's score in THIS segment relative to ALL products competing in it
    product_scores = []
    for c in state.companies:
        for p in c.products:
            s = net_score(p, seg)
            if s > 0:
                product_scores.append({
                    "Company": c.name,
                    "Name": p.name,
                    "Pfmn": p.pfmn,
                    "Size": p.size,
                    "Price": p.price,
                    "MTBF": p.mtbf,
                    "Age": p.age,
                    "Promo": p.promo_budget,
                    "Awareness": p.awareness,
                    "Sales": p.sales_budget,
                    "Accessibility": p.accessibility.get(segment_name, 0),
                    "Cust_Score": s,
                    "Revision_Date": p.revision_date,
                    "_product_ref": p,  # internal — pop before serialize
                })

    # Compute share % within THIS segment
    total_score = sum(p["Cust_Score"] for p in product_scores) or 1
    for p in product_scores:
        p["Market_Share_Pct"] = p["Cust_Score"] / total_score * 100

    # === Estimate per-segment units sold ===
    # Each product's TOTAL units_sold_last is distributed across all segments it competes in,
    # weighted by score share in each segment relative to total score across all segments.
    # Pre-compute total scores for each product across all 4 segments
    for entry in product_scores:
        prod = entry["_product_ref"]
        # Sum this product's net_score across all 4 segments
        units_in_this_seg = prod.segment_sales_last.get(segment_name, 0)
        entry["Units_Sold"] = units_in_this_seg
        # Actual vs Potential: Potential = the units this product's
        # customer-survey score DESERVED (score share × segment demand); Actual = what it
        # sold. Potential > Actual ⇒ under-produced / stocked out (lost sales); Actual >
        # Potential ⇒ windfall from a rival's stock-out.
        potential = int(entry["Market_Share_Pct"] / 100 * total_demand)
        entry["Potential_Units"] = potential
        if potential > 0 and units_in_this_seg < potential * 0.9:
            entry["Demand_Status"] = "Under-served (stock-out)"
        elif units_in_this_seg > potential * 1.1:
            entry["Demand_Status"] = "Windfall"
        else:
            entry["Demand_Status"] = "Balanced"
        # Stock out: True if inventory hit 0 AND production was less than demand
        # Approximation: if inventory = 0 AND units_sold reached production cap
        entry["Stock_Out"] = "YES" if (prod.inventory == 0 and prod.units_sold_last >= prod.production_schedule and prod.production_schedule > 0) else ""

    # Pop internal refs (not JSON-serializable)
    for entry in product_scores:
        entry.pop("_product_ref", None)

    product_scores.sort(key=lambda x: -x["Cust_Score"])

    return {
        "segment": segment_name,
        "industry_demand": total_demand,
        "industry_sold": actual_sold,
        "next_growth": f"{seg.growth_rate*100:.1f}%",
        "ideal_position": {"performance": seg.ideal_pfmn, "size": seg.ideal_size},
        "buying_criteria": {
            "Price": {"range": (seg.price_min, seg.price_max), "weight": f"{seg.price_weight*100:.0f}%"},
            "Age": {"ideal": seg.ideal_age, "weight": f"{seg.age_weight*100:.0f}%"},
            "MTBF": {"range": (seg.mtbf_min, seg.mtbf_max), "weight": f"{seg.mtbf_weight*100:.0f}%"},
            "Position": {"ideal": (seg.ideal_pfmn, seg.ideal_size), "weight": f"{seg.position_weight*100:.0f}%"},
        },
        "top_products": product_scores,
    }


def market_share_report(state: GameState) -> Dict:
    """Total market share by company and by segment."""
    shares = {c.name: {"Thrift": 0, "Core": 0, "Nano": 0, "Elite": 0, "Total": 0}
              for c in state.companies}
    for c in state.companies:
        for p in c.products:
            seg = p.primary_segment
            shares[c.name][seg] += p.units_sold_last
            shares[c.name]["Total"] += p.units_sold_last
    industry_total = sum(s["Total"] for s in shares.values()) or 1
    for cname, sd in shares.items():
        sd["Pct_of_Industry"] = sd["Total"] / industry_total * 100
    return shares


def hr_tqm_report(state: GameState) -> Dict:
    """HR + TQM summary for all 4 companies."""
    data = {}
    for c in state.companies:
        data[c.name] = {
            "Workforce_Complement": c.hr.workforce_complement,
            "First_Shift": c.hr.first_shift_complement,
            "Second_Shift": c.hr.second_shift_complement,
            "Turnover_Rate": f"{c.hr.turnover_rate*100:.1f}%",
            "Recruit_Spend": f"${c.hr.recruit_spend:.0f}",
            "Training_Hours": c.hr.training_hours,
            "Productivity_Index": f"{c.hr.productivity_index:.3f}",
            "HR_Admin_Cost": f"${c.hr.total_hr_admin_cost/1e6:.2f}M",
            "TQM_Round_Spend": f"${sum(c.tqm.spend_this_round.values())/1e6:.1f}M",
            "TQM_Cumulative": f"${c.tqm.total_expenditures/1e6:.1f}M",
            "TQM_Material_Reduction": f"{c.tqm.material_cost_reduction*100:.1f}%",
            "TQM_Labor_Reduction": f"{c.tqm.labor_cost_reduction*100:.1f}%",
            "TQM_Demand_Boost": f"{c.tqm.demand_increase*100:.1f}%",
        }
    return data


def annual_report(company: Company, state: GameState) -> Dict:
    """Annual Report for one company."""
    return {
        "company": company.name,
        "round": state.round_num,
        "year": state.year,
        "balance_sheet": {
            "Cash": company.cash,
            "Accounts_Receivable": company.accounts_receivable,
            "Inventory": company.inventory_value,
            "Total_Current_Assets": company.cash + company.accounts_receivable + company.inventory_value,
            "Plant_Equipment_Gross": company.plant_value,
            "Accumulated_Depreciation": company.accumulated_depreciation,
            "Plant_Equipment_Net": company.plant_value - company.accumulated_depreciation,
            "Total_Assets": company.total_assets,
            "Accounts_Payable": company.accounts_payable,
            "Current_Debt": company.current_debt,
            "Long_Term_Debt": sum(b.face_value for b in company.bonds),
            "Total_Liabilities": company.total_liabilities,
            "Common_Stock": company.common_stock,
            "Retained_Earnings": company.retained_earnings,
            "Total_Equity": company.total_equity,
        },
        "income_statement": {
            "Sales": company.sales_last,
            "Variable_Costs": company.sales_last - company.contribution_margin_last,
            "Contribution_Margin": company.contribution_margin_last,
            "SGA": company.sga_last,
            "EBIT": company.ebit_last,
            "Net_Profit": company.profit_last,
        },
        "products": [
            {
                "Name": p.name,
                "Segment": p.primary_segment,
                "Units_Sold": p.units_sold_last,
                "Revenue": p.revenue_last,
                "Pfmn": p.pfmn, "Size": p.size, "MTBF": p.mtbf,
                "Age": p.age, "Price": p.price,
            } for p in company.products
        ],
        "key_ratios": {
            "ROS": company.ros, "ROA": company.roa, "ROE": company.roe,
            "Asset_Turnover": company.asset_turnover, "Leverage": company.leverage,
            "Stock_Price": company.stock_price, "MarketCap": company.market_cap,
            "EPS": company.eps, "Dividend": company.dividend_per_share,
            "SP_Rating": company.sp_rating,
        }
    }


def full_market_report(state: GameState) -> Dict:
    """Generate the complete market report for the current round."""
    return {
        "round": state.round_num,
        "year": state.year,
        "front_page": front_page(state),
        "stocks_bonds": stocks_bonds_page(state),
        "financial_summary": financial_summary_table(state),
        "production_analysis": production_analysis(state),
        "segments": {
            seg: segment_analysis(state, seg)
            for seg in ["Thrift", "Core", "Nano", "Elite"]
        },
        "market_share": market_share_report(state),
        "hr_tqm": hr_tqm_report(state),
        "annual_reports": {
            c.name: annual_report(c, state) for c in state.companies
        },
    }


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    market_report = full_market_report(state)
    print(f"=== Market Report R{state.round_num} ===\n")
    print("Front Page:")
    for cname, d in market_report["front_page"]["data"].items():
        print(f"  {cname}: Sales {d['Sales']}, Profit {d['Profits']}, ROS {d['ROS']}, ROE {d['ROE']}, Stock ${d.get('Stock','?')}")
    print(f"\nTotal segments analyzed: {len(market_report['segments'])}")
    print(f"Total bonds tracked: {len(market_report['stocks_bonds']['bonds'])}")
    print(f"Total products: {len(market_report['production_analysis'])}")
    print("\nThrift Top Products (top 5):")
    for p in market_report["segments"]["Thrift"]["top_products"][:5]:
        print(f"  {p['Name']} ({p['Company']}): score {p['Cust_Score']:.1f}, share {p['Market_Share_Pct']:.1f}%")
