"""
Pydantic data models for Comp-XM 2026 simulator.

Conventions:
- Money in $ (full dollars, not thousands) unless _k suffix
- Units in actual units (not thousands)
- Percent fields as fraction 0-1 (not 0-100) unless _pct suffix
- Dates as ISO YYYY-MM-DD strings
"""
from __future__ import annotations
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import date


# ============================================================
# SEGMENTS
# ============================================================

SegmentName = Literal["Thrift", "Core", "Nano", "Elite"]
CompanyName = Literal["Andrews", "Baldwin", "Chester", "Digby"]


class Segment(BaseModel):
    """A market segment with ideal-spot, drift, buying criteria, growth rate."""
    name: SegmentName
    # Position at end of CURRENT round (R0 = Dec 31 2025)
    center_pfmn: float
    center_size: float
    # Drift vector applied each year (start-of-year + drift = end-of-year center)
    drift_pfmn: float
    drift_size: float
    # Ideal spot offset from segment center (e.g., Nano = +0.8 pfmn, -1.1 size)
    ideal_offset_pfmn: float
    ideal_offset_size: float
    # Customer buying criteria
    price_min: float
    price_max: float
    price_weight: float       # importance fraction (e.g., 0.55)
    ideal_age: float          # preferred age in years
    age_weight: float
    mtbf_min: int
    mtbf_max: int
    mtbf_weight: float
    position_weight: float
    # Growth rate for NEXT year's demand (multiplicative)
    growth_rate: float        # e.g., 0.11 for 11%

    @property
    def ideal_pfmn(self) -> float:
        return self.center_pfmn + self.ideal_offset_pfmn

    @property
    def ideal_size(self) -> float:
        return self.center_size + self.ideal_offset_size


# ============================================================
# PRODUCTS
# ============================================================

class Product(BaseModel):
    """A sensor product owned by one company."""
    name: str
    company: CompanyName
    primary_segment: SegmentName

    # Position & specs
    pfmn: float
    size: float
    mtbf: int                         # 1000-25000+
    revision_date: str                # YYYY-MM-DD of last revise (or future = in progress)
    age: float                        # years (current age at end of round)

    # Pricing & marketing
    price: float
    promo_budget: float               # dollars
    sales_budget: float               # dollars
    awareness: float = 0.0            # 0..1
    accessibility: Dict[str, float] = Field(default_factory=dict)  # segment -> 0..1

    # Production
    automation: float                 # 1.0 .. 10.0
    capacity_first_shift: int         # units of first-shift capacity per year (1000 units = 1)
    production_schedule: int = 0      # units to produce this round
    inventory: int = 0                # units carried at start of round

    # Cost (per unit) — recomputed by production engine
    material_cost: float = 0.0
    labor_cost: float = 0.0

    # R&D in-progress
    rd_target_pfmn: Optional[float] = None
    rd_target_size: Optional[float] = None
    rd_target_mtbf: Optional[int] = None
    rd_completion_date: Optional[str] = None

    # Last-round results (filled by round engine)
    units_sold_last: int = 0
    units_produced_last: int = 0
    revenue_last: float = 0.0
    contribution_margin_last: float = 0.0
    forecast_last: int = 0           # forecast that was entered for the last round


# ============================================================
# BONDS
# ============================================================

class Bond(BaseModel):
    series: str               # e.g., "13.5S2027"
    face_value: float         # dollars
    coupon_rate: float        # annual interest rate, fraction (0.135)
    year_due: int             # maturity year
    market_close: float = 100.0  # current market price per $100 face
    yield_to_maturity: float = 0.0


# ============================================================
# HR & TQM
# ============================================================

class HRState(BaseModel):
    """OLD Comp-XM HR: Complement + Recruit Spend + Training Hours."""
    workforce_complement: int = 0     # Total needed across all production
    needed_complement: int = 0
    first_shift_complement: int = 0
    second_shift_complement: int = 0
    overtime_pct: float = 0.0
    turnover_rate: float = 0.10       # default 10%
    new_employees: int = 0
    separated_employees: int = 0

    recruit_spend: float = 0.0        # $0-$5000 per person (above auto $1000)
    training_hours: int = 0           # 0-80 hours/employee/year
    productivity_index: float = 1.0   # 1.0 = baseline, grows with training

    recruiting_cost: float = 0.0      # total $ this year
    separation_cost: float = 0.0
    training_cost: float = 0.0
    total_hr_admin_cost: float = 0.0


TQMInitiative = Literal[
    "CPI Systems", "Vendor/JIT", "QIT", "Channel Support Systems",
    "Concurrent Engineering", "UNEP Green Programs",
    "Benchmarking", "QFD Effort", "CCE/6 Sigma", "GEMI TQEM"
]


class TQMState(BaseModel):
    """10 TQM initiatives with $0-$2M per round, cap $4M cumulative per initiative."""
    spend_this_round: Dict[str, float] = Field(default_factory=dict)
    cumulative_spend: Dict[str, float] = Field(default_factory=dict)
    total_expenditures: float = 0.0
    # Cumulative impacts (fractions)
    material_cost_reduction: float = 0.0       # max ~11.8%
    labor_cost_reduction: float = 0.0          # max ~14%
    rd_cycle_time_reduction: float = 0.0       # max ~40%
    admin_cost_reduction: float = 0.0          # max ~60%
    demand_increase: float = 0.0               # max ~14.4%


# ============================================================
# COMPANY (full state)
# ============================================================

class Company(BaseModel):
    name: CompanyName
    products: List[Product]
    bonds: List[Bond] = Field(default_factory=list)

    # Balance sheet ($)
    cash: float = 0.0
    accounts_receivable: float = 0.0
    inventory_value: float = 0.0
    plant_value: float = 0.0          # gross
    accumulated_depreciation: float = 0.0
    accounts_payable: float = 0.0
    current_debt: float = 0.0
    common_stock: float = 0.0
    retained_earnings: float = 0.0

    # Stock
    shares_outstanding: int = 0
    stock_price: float = 0.0
    dividend_per_share: float = 0.0
    eps: float = 0.0
    market_cap: float = 0.0

    # Last-year financial summary
    sales_last: float = 0.0
    ebit_last: float = 0.0
    profit_last: float = 0.0
    cumulative_profit: float = 0.0
    sga_last: float = 0.0
    contribution_margin_last: float = 0.0
    ros: float = 0.0                  # Return on Sales
    asset_turnover: float = 0.0
    roa: float = 0.0
    leverage: float = 0.0             # Assets/Equity
    roe: float = 0.0
    emergency_loan: float = 0.0
    sp_rating: str = "BB"

    # HR & TQM
    hr: HRState = Field(default_factory=HRState)
    tqm: TQMState = Field(default_factory=TQMState)

    @property
    def total_assets(self) -> float:
        net_plant = self.plant_value - self.accumulated_depreciation
        return self.cash + self.accounts_receivable + self.inventory_value + net_plant

    @property
    def total_liabilities(self) -> float:
        return (self.accounts_payable + self.current_debt +
                sum(b.face_value for b in self.bonds))

    @property
    def total_equity(self) -> float:
        return self.common_stock + self.retained_earnings

    @property
    def book_value_per_share(self) -> float:
        if self.shares_outstanding == 0:
            return 0.0
        return self.total_equity / self.shares_outstanding


# ============================================================
# DECISIONS (player input per round)
# ============================================================

class ProductDecision(BaseModel):
    """One product's decisions for a round."""
    product_name: str
    # R&D
    new_pfmn: Optional[float] = None
    new_size: Optional[float] = None
    new_mtbf: Optional[int] = None
    # Marketing
    price: Optional[float] = None
    promo_budget: Optional[float] = None
    sales_budget: Optional[float] = None
    forecast: Optional[int] = None            # Sales Forecast (in 000s units) — what YOU predict you'll sell
    # Production
    production_schedule: Optional[int] = None
    # Automation
    new_automation: Optional[float] = None   # buy-up to this level
    # Capacity
    capacity_change: int = 0                  # +buy, -sell (in 1000 units)


class FinanceDecision(BaseModel):
    """Round-level finance decisions."""
    issue_bond: float = 0.0          # face value $
    retire_bond_early: List[str] = Field(default_factory=list)  # series numbers to retire
    issue_stock: float = 0.0         # $ raised
    buyback_stock: float = 0.0       # $ spent
    dividend_per_share: float = 0.0  # $ per share
    current_debt_borrow: float = 0.0
    accounts_payable_lag: int = 30   # days (default 30)
    accounts_receivable_lag: int = 30


class HRDecision(BaseModel):
    recruit_spend: float = 0.0       # $0-5000 per person
    training_hours: int = 0          # 0-80 hours


class TQMDecision(BaseModel):
    initiatives: Dict[str, float] = Field(default_factory=dict)  # initiative -> $ this round


class RoundDecision(BaseModel):
    """All Andrews decisions for one round."""
    round_num: int
    products: List[ProductDecision]
    finance: FinanceDecision = Field(default_factory=FinanceDecision)
    hr: HRDecision = Field(default_factory=HRDecision)
    tqm: TQMDecision = Field(default_factory=TQMDecision)


# ============================================================
# GAME STATE (full snapshot)
# ============================================================

class GameState(BaseModel):
    """Snapshot of the entire simulation at end of a round."""
    round_num: int                    # 0 = R0 (start), 1-4 = after round N
    year: int                         # 2025=R0, 2026=R1, ...
    prime_interest_rate: float = 0.08
    segments: List[Segment]
    companies: List[Company]          # Andrews, Baldwin, Chester, Digby
    industry_unit_demand: Dict[str, int] = Field(default_factory=dict)  # segment -> units
    industry_unit_sold: Dict[str, int] = Field(default_factory=dict)

    # Historical (round-by-round metrics for trending)
    history: List[Dict] = Field(default_factory=list)  # list of round summaries

    def get_company(self, name: str) -> Company:
        for c in self.companies:
            if c.name == name:
                return c
        raise KeyError(f"Company {name} not found")

    def get_segment(self, name: str) -> Segment:
        for s in self.segments:
            if s.name == name:
                return s
        raise KeyError(f"Segment {name} not found")

    def get_product(self, product_name: str) -> Product:
        for c in self.companies:
            for p in c.products:
                if p.name == product_name:
                    return p
        raise KeyError(f"Product {product_name} not found")


# ============================================================
# REPORTS
# ============================================================

class SegmentReport(BaseModel):
    """Per-segment market analysis for the Inquirer."""
    segment: SegmentName
    industry_unit_demand: int
    industry_unit_sold: int
    next_year_growth: float
    top_products: List[Dict]   # list of {name, market_share, units_sold, etc.}


class BSCScore(BaseModel):
    """Balanced Scorecard for one round."""
    round_num: int
    # Per-perspective scores (0-100 each, weighted)
    financial: float = 0.0
    internal_business: float = 0.0
    customer: float = 0.0
    learning_growth: float = 0.0
    total: float = 0.0           # weighted sum (0-1000 for cumulative)

    # Underlying metrics for transparency
    metrics: Dict[str, float] = Field(default_factory=dict)


class BoardQueryQuestion(BaseModel):
    id: str
    round_num: int
    question: str
    options: List[str]
    correct_index: int
    explanation: str = ""
    topic: str = ""


class BoardQueryResult(BaseModel):
    round_num: int
    answers: Dict[str, int] = Field(default_factory=dict)  # question_id -> selected index
    score: int = 0                                          # number correct
    max_score: int = 0
