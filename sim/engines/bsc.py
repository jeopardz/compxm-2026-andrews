"""
Balanced Scorecard scoring engine.

Per Capsim Comp-XM Balanced Scorecard (4 perspectives, ~125 pts each per round
+ 500 pts cumulative final = 1000 total):

Standard per-round BSC (rough approximations from public Capsim docs):

FINANCIAL (per round):
  - Stock Price: 8 pts (target: increase)
  - Profits: 9 pts (target: $5M+)
  - Leverage: 8 pts (target: 1.8-2.8)
  - Contribution Margin: ? (sometimes included)

INTERNAL BUSINESS (per round):
  - Plant Utilization: 5 pts (target: 100-150%)
  - Days of Working Capital: 5 pts (target: 30-90 days)
  - Stock-out Cost: 5 pts (target: minimize)
  - Inventory Carrying Cost: 5 pts (target: minimize)

CUSTOMER (per round):
  - Customer Survey Score: 20 pts (target: increase)
  - Product Count: 5 pts (target: >=3 in-line products)
  - SG&A / Sales: 5 pts (target: 10-15%)
  - Sales Forecast accuracy: 5 pts

LEARNING & GROWTH (per round):
  - Employee Productivity: 7 pts (target: 110%+)
  - Employee Turnover: 6 pts (target: <8%)
  - HR + TQM investment: ~5 pts each

FINAL CUMULATIVE (500 pts):
  - Average Stock Price growth (50 pts)
  - Cumulative Profit (50 pts)
  - Average Contribution Margin (40 pts)
  - Sales growth (40 pts)
  - Customer Survey trend (60 pts)
  - Asset Turnover trend (40 pts)
  - Etc.

NOTE: Real Capsim BSC weights are proprietary; these are approximations.
"""
from __future__ import annotations
from typing import Dict, List
from sim.data_models import Company, GameState, BSCScore
from sim.engines.production import inventory_carry_cost


# Per-round metric weights (sum to ~125 per perspective, 500 total)
WEIGHTS = {
    "financial": {
        "stock_price_growth": 8,    # +1pt per $5 growth, max 8
        "profit": 9,                # +1pt per $1M profit, max 9
        "leverage_in_range": 8,     # 8 if 1.8-2.8, else scaled
        "contribution_margin_pct": 5,  # +1pt per 5% CM, max 5 (target 30%+)
    },
    "internal_business": {
        "plant_utilization": 5,     # 5 if 100-150%, scaled
        "days_working_capital": 5,  # 5 if 30-90 days
        "stockout_cost": 5,         # 5 if 0, drops as stockouts rise
        "inventory_carry": 5,       # 5 if <5% of sales, scales down
    },
    "customer": {
        "customer_survey_score": 20,  # avg customer score / 80 × 20
        "product_count": 5,            # 5 if 4 products in good shape
        "sga_sales_ratio": 5,          # 5 if 10-15%, scaled
        "sales_forecast_accuracy": 5,  # if forecast within 10% of actual
    },
    "learning_growth": {
        "productivity": 7,              # 7 if PI 1.15+
        "turnover": 6,                  # 6 if turnover <8%
        "hr_admin_cost": 5,             # 5 if invest > $1M
        "tqm_investment": 5,            # 5 if cumulative TQM > $4M
    },
}


def stock_price_score(current: float, last_round: float, max_pts: int = 8) -> float:
    growth = current - last_round
    if growth <= 0:
        return 0.0
    return min(max_pts, growth / 5.0 * max_pts / 5)  # +1pt per $5


def profit_score(profit_m: float, max_pts: int = 9) -> float:
    """Profit score: +1pt per $1M, max points at $9M+."""
    return min(max_pts, max(0, profit_m))


def leverage_score(lev: float, max_pts: int = 8) -> float:
    if 1.8 <= lev <= 2.8:
        return float(max_pts)
    # Linear drop outside range
    if lev < 1.8:
        return max(0, max_pts * (lev / 1.8))
    return max(0, max_pts - (lev - 2.8) * 2)


def contribution_margin_score(cm_pct: float, max_pts: int = 5) -> float:
    if cm_pct >= 0.30:
        return float(max_pts)
    return max(0, max_pts * (cm_pct / 0.30))


def plant_util_score(util_pct: float, max_pts: int = 5) -> float:
    if 100 <= util_pct <= 150:
        return float(max_pts)
    if util_pct < 100:
        return max(0, max_pts * (util_pct / 100))
    # Above 150%, penalty
    return max(0, max_pts - (util_pct - 150) / 10)


def working_capital_score(days: float, max_pts: int = 5) -> float:
    if 30 <= days <= 90:
        return float(max_pts)
    if days < 30:
        return max(0, max_pts * (days / 30))
    # Above 90 days = excess
    return max(0, max_pts - (days - 90) / 10)


def stockout_score(stockout_units: int, total_demand: int, max_pts: int = 5) -> float:
    if total_demand <= 0:
        return float(max_pts)
    pct = stockout_units / total_demand
    return max(0, max_pts * (1 - pct * 5))  # 5% stockout = 0 score


def inventory_score(inv_carry_pct_sales: float, max_pts: int = 5) -> float:
    if inv_carry_pct_sales <= 0.05:
        return float(max_pts)
    return max(0, max_pts * (1 - (inv_carry_pct_sales - 0.05) * 10))


def customer_survey_score_bsc(avg_score: float, max_pts: int = 20) -> float:
    """Avg customer survey score / 80 × 20."""
    return min(max_pts, avg_score / 80.0 * max_pts)


def product_count_score(active_products: int, max_pts: int = 5) -> float:
    return min(max_pts, active_products * (max_pts / 4))


def sga_score(sga_pct: float, max_pts: int = 5) -> float:
    if 0.10 <= sga_pct <= 0.15:
        return float(max_pts)
    if sga_pct < 0.10:
        return max(0, max_pts * (sga_pct / 0.10))
    return max(0, max_pts - (sga_pct - 0.15) * 20)


def forecast_score(forecast_units: int, actual_units: int, max_pts: int = 5) -> float:
    if forecast_units <= 0:
        return 0.0
    err = abs(forecast_units - actual_units) / forecast_units
    return max(0, max_pts * (1 - err * 5))  # 20% error = 0


def productivity_score(pi: float, max_pts: int = 7) -> float:
    if pi >= 1.15:
        return float(max_pts)
    return max(0, max_pts * ((pi - 1.0) / 0.15))


def turnover_score(turnover_rate: float, max_pts: int = 6) -> float:
    if turnover_rate <= 0.05:
        return float(max_pts)
    return max(0, max_pts * (1 - (turnover_rate - 0.05) / 0.05))


def hr_invest_score(hr_admin_cost: float, max_pts: int = 5) -> float:
    if hr_admin_cost >= 1_000_000:
        return float(max_pts)
    return max(0, max_pts * (hr_admin_cost / 1_000_000))


def tqm_invest_score(tqm_cumulative: float, max_pts: int = 5) -> float:
    if tqm_cumulative >= 4_000_000:
        return float(max_pts)
    return max(0, max_pts * (tqm_cumulative / 4_000_000))


def compute_round_bsc(state: GameState, company_name: str = "Andrews",
                      prev_state: GameState = None) -> BSCScore:
    """Compute BSC for one round."""
    c = state.get_company(company_name)
    metrics = {}

    # Financial
    last_stock = prev_state.get_company(company_name).stock_price if prev_state else c.stock_price
    fin_stock = stock_price_score(c.stock_price, last_stock)
    fin_profit = profit_score(c.profit_last / 1e6)
    fin_lev = leverage_score(c.leverage)
    cm_pct = c.contribution_margin_last / max(1, c.sales_last)
    fin_cm = contribution_margin_score(cm_pct)
    financial = fin_stock + fin_profit + fin_lev + fin_cm
    metrics.update({
        "fin_stock_price": fin_stock, "fin_profit": fin_profit,
        "fin_leverage": fin_lev, "fin_contribution_margin": fin_cm,
    })

    # Internal Business
    # Plant utilization: average across products
    util_pcts = []
    inv_total = 0
    for p in c.products:
        if p.capacity_first_shift > 0:
            util_pcts.append(p.units_produced_last / p.capacity_first_shift * 100)
        inv_total += p.inventory
    avg_util = sum(util_pcts) / len(util_pcts) if util_pcts else 100

    ib_util = plant_util_score(avg_util)
    # Days working capital: (AR + Inv - AP) / sales * 365
    if c.sales_last > 0:
        days_wc = (c.accounts_receivable + c.inventory_value - c.accounts_payable) / c.sales_last * 365
    else:
        days_wc = 60
    ib_wc = working_capital_score(days_wc)
    ib_stockout = stockout_score(0, sum(p.units_sold_last for p in c.products))  # approx
    inv_carry_total = sum(inventory_carry_cost(p, p.inventory) for p in c.products)
    inv_pct = inv_carry_total / max(1, c.sales_last)
    ib_inv = inventory_score(inv_pct)
    internal_business = ib_util + ib_wc + ib_stockout + ib_inv
    metrics.update({
        "ib_plant_utilization": ib_util, "ib_working_capital": ib_wc,
        "ib_stockout": ib_stockout, "ib_inventory": ib_inv,
    })

    # Customer
    from sim.engines.customer_score import net_score
    cust_scores = []
    for p in c.products:
        seg = state.get_segment(p.primary_segment)
        cust_scores.append(net_score(p, seg))
    avg_cust = sum(cust_scores) / len(cust_scores) if cust_scores else 0
    cu_survey = customer_survey_score_bsc(avg_cust)
    cu_count = product_count_score(len([p for p in c.products if p.units_sold_last > 0]))
    sga_pct = c.sga_last / max(1, c.sales_last)
    cu_sga = sga_score(sga_pct)
    # Forecast accuracy: use Sales Forecast field if set, fallback to production_schedule
    total_forecast = sum(p.forecast_last if p.forecast_last > 0 else p.production_schedule
                          for p in c.products)
    cu_forecast = forecast_score(
        total_forecast,
        sum(p.units_sold_last for p in c.products)
    )
    customer = cu_survey + cu_count + cu_sga + cu_forecast
    metrics.update({
        "cu_customer_survey": cu_survey, "cu_product_count": cu_count,
        "cu_sga": cu_sga, "cu_forecast": cu_forecast,
    })

    # Learning & Growth
    lg_pi = productivity_score(c.hr.productivity_index)
    lg_to = turnover_score(c.hr.turnover_rate)
    lg_hr = hr_invest_score(c.hr.total_hr_admin_cost)
    lg_tqm = tqm_invest_score(c.tqm.total_expenditures)
    learning_growth = lg_pi + lg_to + lg_hr + lg_tqm
    metrics.update({
        "lg_productivity": lg_pi, "lg_turnover": lg_to,
        "lg_hr_invest": lg_hr, "lg_tqm_invest": lg_tqm,
    })

    total = financial + internal_business + customer + learning_growth

    return BSCScore(
        round_num=state.round_num,
        financial=financial,
        internal_business=internal_business,
        customer=customer,
        learning_growth=learning_growth,
        total=total,
        metrics=metrics,
    )


def compute_cumulative_bsc(history, state: GameState,
                            company_name: str = "Andrews") -> BSCScore:
    """
    Final cumulative BSC (500 pts, evaluated after R4).
    Based on average + trend across all 4 rounds.

    history: list of BSCScore objects OR dicts (model_dump).
    """
    if not history:
        return BSCScore(round_num=5, financial=0, internal_business=0,
                         customer=0, learning_growth=0, total=0)

    # Normalize history: accept both BSCScore objects and dicts
    def _metrics(h):
        if isinstance(h, dict):
            return h.get("metrics", {})
        return h.metrics

    c = state.get_company(company_name)
    metrics = {}

    # Financial: cumulative profit + stock growth
    cum_profit_m = c.cumulative_profit / 1e6
    fin_cum_profit = min(100, cum_profit_m)  # +1pt per $1M, cap $100M = 100
    # Initial stock $95.38 (R0), score by current vs initial
    fin_stock_growth = min(50, max(0, (c.stock_price - 95.38) * 0.5))
    fin_avg_roe = min(50, c.roe * 200)  # 25% ROE = 50 pts
    financial = fin_cum_profit + fin_stock_growth + fin_avg_roe

    # Internal Business: avg utilization, avg inventory mgmt
    avg_util = sum(_metrics(h).get("ib_plant_utilization", 0) for h in history) / len(history)
    avg_wc = sum(_metrics(h).get("ib_working_capital", 0) for h in history) / len(history)
    avg_stock = sum(_metrics(h).get("ib_stockout", 0) for h in history) / len(history)
    avg_inv = sum(_metrics(h).get("ib_inventory", 0) for h in history) / len(history)
    internal_business = (avg_util + avg_wc + avg_stock + avg_inv) * 5  # scale to 100 max

    # Customer: avg survey, market share
    avg_survey = sum(_metrics(h).get("cu_customer_survey", 0) for h in history) / len(history)
    customer = avg_survey * 5  # max 100

    # Learning & Growth: max PI achieved, total TQM
    lg_max_pi = (c.hr.productivity_index - 1.0) * 250  # PI 1.20 = 50 pts
    lg_tqm = min(50, c.tqm.total_expenditures / 1e6 * 5)  # $10M+ = 50 pts
    learning_growth = lg_max_pi + lg_tqm

    total = financial + internal_business + customer + learning_growth

    return BSCScore(
        round_num=5,
        financial=financial,
        internal_business=internal_business,
        customer=customer,
        learning_growth=learning_growth,
        total=total,
        metrics={
            "cumulative_profit_m": cum_profit_m,
            "final_stock": c.stock_price,
            "final_roe": c.roe,
            "max_pi": c.hr.productivity_index,
            "total_tqm_m": c.tqm.total_expenditures / 1e6,
        },
    )


if __name__ == "__main__":
    from sim.data.r0_seed import build_r0_state
    state = build_r0_state()
    bsc = compute_round_bsc(state, "Andrews")
    print("=== Andrews R0 BSC ===")
    print(f"Financial:         {bsc.financial:.1f}")
    print(f"Internal Business: {bsc.internal_business:.1f}")
    print(f"Customer:          {bsc.customer:.1f}")
    print(f"Learning & Growth: {bsc.learning_growth:.1f}")
    print(f"TOTAL ROUND SCORE: {bsc.total:.1f}/125")
    print("\nMetric breakdown:")
    for k, v in bsc.metrics.items():
        print(f"  {k}: {v:.1f}")
