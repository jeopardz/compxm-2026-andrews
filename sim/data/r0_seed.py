"""
R0 (Dec 31, 2025) starting state for Comp-XM 2026 Andrews simulation.
Data sourced from:
  - Comp-XM Industry Conditions Report 2026 (segments, drift, growth, buying criteria)
  - Comp-XM Inquirer Report 2026 R0 (companies, products, financials, bonds)
"""
from sim.data_models import (
    Segment, Product, Company, Bond, GameState, HRState, TQMState,
)


# ============================================================
# SEGMENTS (R0 = end of 2025, Industry Conditions Report)
# ============================================================
SEGMENTS = [
    Segment(
        name="Thrift",
        center_pfmn=5.7, center_size=14.3,
        drift_pfmn=0.5, drift_size=-0.5,
        ideal_offset_pfmn=0.0, ideal_offset_size=0.0,
        price_min=14.0, price_max=26.0, price_weight=0.55,
        ideal_age=3.0, age_weight=0.10,
        mtbf_min=14000, mtbf_max=20000, mtbf_weight=0.20,
        position_weight=0.15,
        growth_rate=0.11,
    ),
    Segment(
        name="Core",
        center_pfmn=7.4, center_size=12.6,
        drift_pfmn=0.8, drift_size=-0.8,
        ideal_offset_pfmn=0.4, ideal_offset_size=-0.4,
        price_min=20.0, price_max=32.0, price_weight=0.46,
        ideal_age=2.0, age_weight=0.20,
        mtbf_min=16000, mtbf_max=22000, mtbf_weight=0.18,
        position_weight=0.16,
        growth_rate=0.10,
    ),
    Segment(
        name="Nano",
        center_pfmn=8.9, center_size=9.4,
        drift_pfmn=0.8, drift_size=-1.1,
        ideal_offset_pfmn=0.8, ideal_offset_size=-1.1,
        price_min=28.0, price_max=40.0, price_weight=0.27,
        ideal_age=1.0, age_weight=0.20,
        mtbf_min=18000, mtbf_max=24000, mtbf_weight=0.18,
        position_weight=0.35,
        growth_rate=0.14,
    ),
    Segment(
        name="Elite",
        center_pfmn=10.6, center_size=11.1,
        drift_pfmn=1.1, drift_size=-0.8,
        ideal_offset_pfmn=1.1, ideal_offset_size=-0.8,
        price_min=30.0, price_max=42.0, price_weight=0.24,
        ideal_age=0.0, age_weight=0.34,
        mtbf_min=20000, mtbf_max=26000, mtbf_weight=0.20,
        position_weight=0.22,
        growth_rate=0.16,
    ),
]


# ============================================================
# PRODUCTS by company (R0 state, from Inquirer Production Analysis)
# ============================================================

# --- ANDREWS (Broad, leading) ---
ANDREWS_PRODUCTS = [
    Product(
        name="Attic", company="Andrews", primary_segment="Thrift",
        pfmn=4.9, size=15.1, mtbf=20000,
        revision_date="2023-04-13", age=5.1,
        price=26.00, promo_budget=1050000, sales_budget=600000,
        automation=6.0, capacity_first_shift=1130,
        inventory=761, units_sold_last=1368, units_produced_last=1100,
        material_cost=8.13, labor_cost=7.90,
        awareness=0.62, accessibility={"Thrift": 0.74},
    ),
    Product(
        name="Axe", company="Andrews", primary_segment="Core",
        pfmn=7.6, size=12.4, mtbf=22000,
        revision_date="2024-12-09", age=2.2,
        price=32.00, promo_budget=1200000, sales_budget=1000000,
        automation=5.0, capacity_first_shift=1200,
        inventory=54, units_sold_last=1827, units_produced_last=1650,
        material_cost=11.60, labor_cost=8.96,
        awareness=0.80, accessibility={"Core": 0.85},
    ),
    Product(
        name="Art", company="Andrews", primary_segment="Nano",
        pfmn=10.3, size=7.8, mtbf=24000,
        revision_date="2025-11-09", age=1.1,
        price=40.00, promo_budget=1200000, sales_budget=1000000,
        automation=4.0, capacity_first_shift=728,
        inventory=267, units_sold_last=921, units_produced_last=950,
        material_cost=16.13, labor_cost=10.29,
        awareness=0.78, accessibility={"Nano": 0.82},
    ),
    Product(
        name="Ant", company="Andrews", primary_segment="Elite",
        pfmn=12.4, size=9.8, mtbf=26000,
        revision_date="2025-11-14", age=1.1,
        price=42.00, promo_budget=1200000, sales_budget=1000000,
        automation=4.0, capacity_first_shift=714,
        inventory=219, units_sold_last=772, units_produced_last=850,
        material_cost=16.81, labor_cost=9.80,
        awareness=0.77, accessibility={"Elite": 0.87},
    ),
]

# --- BALDWIN (Niche High Tech: Nano+Elite) ---
BALDWIN_PRODUCTS = [
    Product(
        name="Best", company="Baldwin", primary_segment="Nano",
        pfmn=8.6, size=9.6, mtbf=23000,
        revision_date="2025-11-12", age=2.2,
        price=30.00, promo_budget=1100000, sales_budget=1200000,
        automation=5.0, capacity_first_shift=570,
        inventory=91, units_sold_last=1127, units_produced_last=1100,
        material_cost=13.98, labor_cost=9.50,
        awareness=0.70, accessibility={"Nano": 0.81},
    ),
    Product(
        name="Bam", company="Baldwin", primary_segment="Elite",
        pfmn=11.8, size=9.8, mtbf=25000,
        revision_date="2025-12-13", age=1.9,
        price=39.00, promo_budget=950000, sales_budget=1000000,
        automation=5.0, capacity_first_shift=950,
        inventory=149, units_sold_last=435, units_produced_last=480,
        material_cost=16.39, labor_cost=7.95,
        awareness=0.72, accessibility={"Elite": 0.81},
    ),
    Product(
        name="Bell", company="Baldwin", primary_segment="Nano",
        pfmn=10.2, size=7.8, mtbf=23000,
        revision_date="2025-12-22", age=1.0,
        price=37.00, promo_budget=1200000, sales_budget=600000,
        automation=5.0, capacity_first_shift=850,
        inventory=215, units_sold_last=959, units_produced_last=950,
        material_cost=15.79, labor_cost=8.50,
        awareness=0.69, accessibility={"Nano": 0.66},
    ),
    Product(
        name="Bit", company="Baldwin", primary_segment="Elite",
        pfmn=12.2, size=9.8, mtbf=25000,
        revision_date="2025-12-05", age=1.0,
        price=42.00, promo_budget=1100000, sales_budget=1200000,
        automation=5.0, capacity_first_shift=850,
        inventory=194, units_sold_last=864, units_produced_last=900,
        material_cost=16.81, labor_cost=9.80,
        awareness=0.69, accessibility={"Elite": 0.87},
    ),
]

# --- CHESTER (Niche Low Tech: Thrift+Core) ---
CHESTER_PRODUCTS = [
    Product(
        name="Creak", company="Chester", primary_segment="Thrift",
        pfmn=6.0, size=14.0, mtbf=17000,
        revision_date="2025-12-11", age=2.8,
        price=19.00, promo_budget=1050000, sales_budget=1000000,
        automation=8.0, capacity_first_shift=1050,
        inventory=240, units_sold_last=1338, units_produced_last=1250,
        material_cost=8.40, labor_cost=4.03,
        awareness=0.63, accessibility={"Thrift": 0.62},
    ),
    Product(
        name="Cat", company="Chester", primary_segment="Thrift",
        pfmn=6.2, size=13.8, mtbf=17000,
        revision_date="2025-12-19", age=2.6,
        price=19.00, promo_budget=1050000, sales_budget=800000,
        automation=8.0, capacity_first_shift=1250,
        inventory=290, units_sold_last=1671, units_produced_last=1600,
        material_cost=8.61, labor_cost=4.22,
        awareness=0.63, accessibility={"Thrift": 0.62},
    ),
    Product(
        name="Cent", company="Chester", primary_segment="Core",
        pfmn=8.6, size=11.0, mtbf=18000,
        revision_date="2025-12-03", age=1.2,
        price=27.00, promo_budget=1100000, sales_budget=400000,
        automation=6.0, capacity_first_shift=900,
        inventory=152, units_sold_last=1287, units_produced_last=1300,
        material_cost=11.68, labor_cost=7.38,
        awareness=0.71, accessibility={"Core": 0.58},
    ),
    Product(
        name="City", company="Chester", primary_segment="Core",
        pfmn=9.3, size=11.5, mtbf=20000,
        revision_date="2025-11-19", age=1.2,
        price=28.00, promo_budget=1050000, sales_budget=600000,
        automation=6.0, capacity_first_shift=950,
        inventory=87, units_sold_last=1414, units_produced_last=1450,
        material_cost=12.39, labor_cost=7.38,
        awareness=0.63, accessibility={"Core": 0.58},
    ),
]

# --- DIGBY (Broad: all 4 segments) ---
DIGBY_PRODUCTS = [
    Product(
        name="Drum", company="Digby", primary_segment="Thrift",
        pfmn=5.2, size=14.8, mtbf=14000,
        revision_date="2026-06-28", age=3.5,  # in-progress revision
        price=20.00, promo_budget=1050000, sales_budget=1000000,
        automation=9.0, capacity_first_shift=1000,
        inventory=22, units_sold_last=1730, units_produced_last=1700,
        material_cost=6.65, labor_cost=2.82,
        awareness=0.52, accessibility={"Thrift": 0.63},
    ),
    Product(
        name="Daft", company="Digby", primary_segment="Core",
        pfmn=7.8, size=12.2, mtbf=16000,
        revision_date="2025-11-30", age=1.2,
        price=22.00, promo_budget=1050000, sales_budget=600000,
        automation=7.0, capacity_first_shift=1150,
        inventory=14, units_sold_last=1885, units_produced_last=1900,
        material_cost=10.01, labor_cost=5.64,
        awareness=0.52, accessibility={"Core": 0.62},
    ),
    Product(
        name="Deal", company="Digby", primary_segment="Nano",
        pfmn=9.7, size=8.5, mtbf=18000,
        revision_date="2025-12-22", age=1.1,
        price=31.00, promo_budget=1100000, sales_budget=1300000,
        automation=6.0, capacity_first_shift=750,
        inventory=161, units_sold_last=604, units_produced_last=700,
        material_cost=13.64, labor_cost=6.24,
        awareness=0.53, accessibility={"Nano": 0.81},
    ),
    Product(
        name="Dino", company="Digby", primary_segment="Elite",
        pfmn=11.7, size=10.3, mtbf=20000,
        revision_date="2025-11-05", age=1.1,
        price=35.00, promo_budget=1050000, sales_budget=600000,
        automation=5.0, capacity_first_shift=800,
        inventory=137, units_sold_last=700, units_produced_last=800,
        material_cost=14.36, labor_cost=7.09,
        awareness=0.52, accessibility={"Elite": 0.81},
    ),
]


# ============================================================
# BONDS (from Inquirer R0 Stock & Bond Market Summary)
# ============================================================

ANDREWS_BONDS = [
    Bond(series="13.5S2027", face_value=11_300_000, coupon_rate=0.135,
         year_due=2027, market_close=103.58, yield_to_maturity=0.130),
    Bond(series="11.2S2032", face_value=8_837_000, coupon_rate=0.112,
         year_due=2032, market_close=99.07, yield_to_maturity=0.113),
    Bond(series="11.9S2033", face_value=7_072_000, coupon_rate=0.119,
         year_due=2033, market_close=102.54, yield_to_maturity=0.116),
]

BALDWIN_BONDS = [
    Bond(series="13.5S2027", face_value=11_300_000, coupon_rate=0.135,
         year_due=2027, market_close=102.54, yield_to_maturity=0.132),
    Bond(series="11.1S2034", face_value=2_425_572, coupon_rate=0.111,
         year_due=2034, market_close=95.21, yield_to_maturity=0.117),
    Bond(series="11.2S2035", face_value=5_785_949, coupon_rate=0.112,
         year_due=2035, market_close=95.48, yield_to_maturity=0.117),
]

CHESTER_BONDS = [
    Bond(series="13.5S2027", face_value=11_300_000, coupon_rate=0.135,
         year_due=2027, market_close=100.17, yield_to_maturity=0.135),
    Bond(series="11.3S2032", face_value=10_417_600, coupon_rate=0.113,
         year_due=2032, market_close=90.83, yield_to_maturity=0.124),
    Bond(series="12.5S2033", face_value=14_665_611, coupon_rate=0.125,
         year_due=2033, market_close=95.74, yield_to_maturity=0.131),
    Bond(series="12.5S2034", face_value=7_987_653, coupon_rate=0.125,
         year_due=2034, market_close=95.45, yield_to_maturity=0.131),
    Bond(series="12.5S2035", face_value=9_474_381, coupon_rate=0.125,
         year_due=2035, market_close=95.19, yield_to_maturity=0.131),
]

DIGBY_BONDS = [
    Bond(series="13.5S2027", face_value=11_300_000, coupon_rate=0.135,
         year_due=2027, market_close=100.83, yield_to_maturity=0.134),
    Bond(series="11.2S2032", face_value=8_607_404, coupon_rate=0.112,
         year_due=2032, market_close=92.04, yield_to_maturity=0.122),
    Bond(series="12.4S2033", face_value=5_756_951, coupon_rate=0.124,
         year_due=2033, market_close=97.12, yield_to_maturity=0.128),
    Bond(series="11.9S2035", face_value=15_689_911, coupon_rate=0.119,
         year_due=2035, market_close=94.03, yield_to_maturity=0.127),
]


# ============================================================
# COMPANIES (R0 financial state from Inquirer Annual Reports)
# ============================================================

ANDREWS = Company(
    name="Andrews",
    products=ANDREWS_PRODUCTS,
    bonds=ANDREWS_BONDS,
    cash=31_543_000,
    accounts_receivable=13_421_000,
    inventory_value=26_149_000,
    plant_value=96_824_000,
    accumulated_depreciation=44_409_000,
    accounts_payable=9_516_000,
    current_debt=15_717_000,
    common_stock=12_080_000,
    retained_earnings=59_004_000,
    shares_outstanding=2_051_289,
    stock_price=95.38,
    dividend_per_share=6.50,
    eps=9.80,
    market_cap=196_000_000,
    sales_last=163_291_000,
    ebit_last=36_406_000,
    profit_last=20_101_000,
    cumulative_profit=20_101_000,  # approximate; need historical sum
    sga_last=12_833_000,
    contribution_margin_last=55_723_000,
    ros=0.123,
    asset_turnover=1.32,
    roa=0.163,
    leverage=1.74,
    roe=0.283,
    emergency_loan=0,
    sp_rating="BB",
    hr=HRState(
        workforce_complement=804,
        needed_complement=804,
        first_shift_complement=525,
        second_shift_complement=279,
        overtime_pct=0.0,
        turnover_rate=0.10,
        new_employees=140,
        separated_employees=0,
        recruit_spend=0,
        training_hours=0,
        productivity_index=1.0,
    ),
    tqm=TQMState(),
)

BALDWIN = Company(
    name="Baldwin",
    products=BALDWIN_PRODUCTS,
    bonds=BALDWIN_BONDS,
    cash=19_378_000,
    accounts_receivable=9_824_000,
    inventory_value=14_997_000,
    plant_value=84_380_000,
    accumulated_depreciation=35_023_000,
    accounts_payable=6_382_000,
    current_debt=18_303_000,
    common_stock=9_091_000,
    retained_earnings=40_269_000,
    shares_outstanding=1_909_064,
    stock_price=55.73,
    dividend_per_share=2.37,
    eps=5.79,
    market_cap=106_000_000,
    sales_last=119_521_000,
    ebit_last=21_589_000,
    profit_last=11_054_000,
    cumulative_profit=11_054_000,
    sga_last=21_590_000,
    contribution_margin_last=39_826_000,
    ros=0.092,
    asset_turnover=1.28,
    roa=0.118,
    leverage=1.90,
    roe=0.224,
    emergency_loan=0,
    sp_rating="BB",
    hr=HRState(
        workforce_complement=483,
        first_shift_complement=371,
        second_shift_complement=112,
        recruit_spend=0,
        training_hours=0,
        productivity_index=1.0,
    ),
)

CHESTER = Company(
    name="Chester",
    products=CHESTER_PRODUCTS,
    bonds=CHESTER_BONDS,
    cash=31_960_000,
    accounts_receivable=10_809_000,
    inventory_value=10_603_000,
    plant_value=142_900_000,
    accumulated_depreciation=51_265_000,
    accounts_payable=7_459_000,
    current_debt=29_231_000,
    common_stock=29_958_000,
    retained_earnings=54_648_000,
    shares_outstanding=2_566_964,
    stock_price=44.50,
    dividend_per_share=4.93,
    eps=2.91,
    market_cap=114_000_000,
    sales_last=131_510_000,
    ebit_last=21_673_000,
    profit_last=7_459_000,
    cumulative_profit=7_459_000,
    sga_last=21_673_000,
    contribution_margin_last=44_384_000,
    ros=0.057,
    asset_turnover=0.91,
    roa=0.051,
    leverage=2.70,
    roe=0.137,
    emergency_loan=0,
    sp_rating="B",
    hr=HRState(
        workforce_complement=539,
        first_shift_complement=316,
        second_shift_complement=223,
        recruit_spend=2500,
        training_hours=40,
        productivity_index=1.094,
    ),
)

DIGBY = Company(
    name="Digby",
    products=DIGBY_PRODUCTS,
    bonds=DIGBY_BONDS,
    cash=32_632_000,
    accounts_receivable=9_773_000,
    inventory_value=6_437_000,
    plant_value=125_952_000,
    accumulated_depreciation=47_289_000,
    accounts_payable=10_205_000,
    current_debt=25_558_000,
    common_stock=14_328_000,
    retained_earnings=53_243_000,
    shares_outstanding=2_171_290,
    stock_price=53.17,
    dividend_per_share=2.84,
    eps=4.70,
    market_cap=115_000_000,
    sales_last=118_899_000,
    ebit_last=23_774_000,
    profit_last=10_205_000,
    cumulative_profit=10_205_000,
    sga_last=23_774_000,
    contribution_margin_last=46_118_000,
    ros=0.086,
    asset_turnover=0.94,
    roa=0.081,
    leverage=2.40,
    roe=0.194,
    emergency_loan=0,
    sp_rating="B",
    hr=HRState(
        workforce_complement=398,
        first_shift_complement=260,
        second_shift_complement=138,
        recruit_spend=5000,
        training_hours=80,
        productivity_index=1.176,
    ),
)


# ============================================================
# Industry-level R0 stats
# ============================================================

R0_INDUSTRY_DEMAND = {
    "Thrift": 5101,
    "Core": 6676,
    "Nano": 3648,
    "Elite": 3476,
}

R0_INDUSTRY_SOLD = R0_INDUSTRY_DEMAND.copy()  # no stockouts in R0


def build_r0_state() -> GameState:
    """Return a fresh R0 GameState (Dec 31, 2025)."""
    return GameState(
        round_num=0,
        year=2025,
        prime_interest_rate=0.08,
        segments=[s.model_copy(deep=True) for s in SEGMENTS],
        companies=[
            ANDREWS.model_copy(deep=True),
            BALDWIN.model_copy(deep=True),
            CHESTER.model_copy(deep=True),
            DIGBY.model_copy(deep=True),
        ],
        industry_unit_demand=R0_INDUSTRY_DEMAND.copy(),
        industry_unit_sold=R0_INDUSTRY_SOLD.copy(),
        history=[],
    )


if __name__ == "__main__":
    state = build_r0_state()
    print(f"R0 State: Round {state.round_num}, Year {state.year}")
    print(f"Companies: {[c.name for c in state.companies]}")
    print(f"Andrews products: {[p.name for p in state.get_company('Andrews').products]}")
    print(f"Andrews Cash: ${state.get_company('Andrews').cash/1e6:.1f}M")
    print(f"Andrews Stock: ${state.get_company('Andrews').stock_price:.2f}")
    print(f"Total industry demand: {sum(state.industry_unit_demand.values())} units")
    for seg in state.segments:
        print(f"  {seg.name}: center ({seg.center_pfmn},{seg.center_size}) "
              f"ideal ({seg.ideal_pfmn:.1f},{seg.ideal_size:.1f}) growth {seg.growth_rate*100:.0f}%")
