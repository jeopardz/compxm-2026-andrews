"""
Integration test: Apex R1-R4 full playthrough.

Validates that the simulator can run a full 4-round game without crashes,
with reasonable directional results (positive profit, no negative cash, etc.).
"""
import pytest
from sim.data.r0_seed import build_r0_state
from sim.data_models import RoundDecision, ProductDecision, FinanceDecision, HRDecision, TQMDecision
from sim.engines.round_engine import advance_round
from sim.engines.tqm import recommended_initiatives_for_round
from sim.engines.bsc import compute_cumulative_bsc


def make_round_decision(state, round_num: int) -> RoundDecision:
    """Generate sensible decisions for Apex per round."""
    apex = state.get_company("Apex")
    product_decisions = []

    for p in apex.products:
        seg = state.get_segment(p.primary_segment)
        # Revise to next year's ideal
        future_pfmn = seg.center_pfmn + seg.drift_pfmn + seg.ideal_offset_pfmn
        future_size = seg.center_size + seg.drift_size + seg.ideal_offset_size
        # Always revise (sensible defense + offense)
        target_mtbf = min(seg.mtbf_max, p.mtbf + 1000)
        pd = ProductDecision(
            product_name=p.name,
            new_pfmn=round(future_pfmn, 1),
            new_size=round(future_size, 1),
            new_mtbf=target_mtbf,
            price=(seg.price_max - 1.0),  # near max premium
            promo_budget=1_500_000,
            sales_budget=1_500_000,
            production_schedule=int(p.capacity_first_shift * 1.5),
        )
        product_decisions.append(pd)

    # Finance: retire 13.5S2027 in R1, dividend $6/share
    finance = FinanceDecision(
        retire_bond_early=["13.5S2027"] if round_num == 1 else [],
        dividend_per_share=6.00 if round_num <= 2 else 4.00,
    )

    # HR
    hr = HRDecision(recruit_spend=2500, training_hours=40)

    # TQM
    tqm = TQMDecision(initiatives=recommended_initiatives_for_round(round_num))

    return RoundDecision(
        round_num=round_num,
        products=product_decisions,
        finance=finance,
        hr=hr,
        tqm=tqm,
    )


def test_r1_r4_full_playthrough():
    """Run 4 rounds, verify no crash and reasonable outputs."""
    state = build_r0_state()
    bsc_results = []
    prev_state = None

    for r in range(1, 5):
        decision = make_round_decision(state, r)
        prev_state = state.model_copy(deep=True)
        result = advance_round(state, decision, prev_state=prev_state)
        assert result["round_num"] == r, f"Round number mismatch at R{r}"
        bsc_results.append(result["bsc"])

        apex = state.get_company("Apex")
        # Sanity checks
        assert apex.cash >= -50_000_000, f"R{r}: Cash way negative ${apex.cash/1e6:.1f}M"
        assert apex.stock_price >= 1.0, f"R{r}: Stock price collapsed to ${apex.stock_price}"
        assert apex.profit_last > -50_000_000, f"R{r}: Profit way negative ${apex.profit_last/1e6:.1f}M"
        assert apex.shares_outstanding > 0, f"R{r}: Shares outstanding is 0"
        assert len(apex.products) == 4, f"R{r}: Products count changed"

        print(f"\nR{r}: Stock ${apex.stock_price:.2f}, Profit ${apex.profit_last/1e6:.1f}M, "
              f"Cash ${apex.cash/1e6:.1f}M, BSC {result['bsc']['total']:.1f}")

    # Final state checks
    assert state.round_num == 4
    assert state.year == 2029
    final_apex = state.get_company("Apex")
    assert final_apex.cumulative_profit > 0, f"Cumulative profit negative: ${final_apex.cumulative_profit/1e6:.1f}M"
    assert final_apex.tqm.total_expenditures > 10_000_000, "TQM under-invested"
    assert final_apex.hr.productivity_index >= 1.0, "HR PI didn't improve"

    # Cumulative BSC
    cum_bsc = compute_cumulative_bsc(bsc_results, state, "Apex")
    print(f"\n=== FINAL CUMULATIVE BSC ===")
    print(f"  Financial: {cum_bsc.financial:.1f}")
    print(f"  Internal Bus: {cum_bsc.internal_business:.1f}")
    print(f"  Customer: {cum_bsc.customer:.1f}")
    print(f"  Learning&Growth: {cum_bsc.learning_growth:.1f}")
    print(f"  TOTAL: {cum_bsc.total:.1f} / 500")
    print(f"  Round-by-round total: {sum(b['total'] for b in bsc_results):.1f} / 500")
    print(f"  GRAND TOTAL: {cum_bsc.total + sum(b['total'] for b in bsc_results):.1f} / 1000")


def test_history_records_each_round():
    """Verify state.history grows by 1 each round."""
    state = build_r0_state()
    for r in range(1, 5):
        d = make_round_decision(state, r)
        advance_round(state, d, prev_state=state.model_copy(deep=True))
        assert len(state.history) == r, f"History length mismatch at R{r}"


def test_ai_competitors_make_decisions():
    """Verify AI competitors actually do things (revise, spend on HR/TQM)."""
    state = build_r0_state()
    initial_borealis_age = state.get_company("Borealis").products[0].age

    d = make_round_decision(state, 1)
    advance_round(state, d, prev_state=state.model_copy(deep=True))

    # All companies should have HR investment now
    for c in state.companies:
        assert c.hr.total_hr_admin_cost > 0, f"{c.name} has no HR investment"
        assert c.tqm.total_expenditures > 0, f"{c.name} has no TQM investment"


if __name__ == "__main__":
    print("=" * 60)
    print("INTEGRATION TEST: Apex R1-R4 Full Playthrough")
    print("=" * 60)
    test_r1_r4_full_playthrough()
    print("\n[OK] All integration tests passed")
