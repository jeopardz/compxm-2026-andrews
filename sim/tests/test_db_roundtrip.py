"""Serialization round-trip tests for the DB persistence layer.

The SaaS build stores game state as jsonb: GameState.model_dump() ->
game_snapshots.state_json and RoundDecision.model_dump() -> pending_json. These
tests exercise that exact path (Pydantic -> JSON text -> Pydantic) WITHOUT a live
database, guaranteeing a snapshot written to Postgres reloads into an identical,
still-playable game. They also confirm the SaaS modules import without supabase.
"""
from __future__ import annotations

import json
from copy import deepcopy

from sim.data.r0_seed import build_r0_state
from sim.data.scenarios import generate_scenario
from sim.data_models import GameState, ProductDecision, RoundDecision
from sim.engines.round_engine import advance_round


def _json_round_trip(model):
    """Mimic jsonb storage: dump -> JSON text -> load -> validate."""
    text = json.dumps(model.model_dump(), default=str)
    return type(model).model_validate(json.loads(text))


class TestGameStateRoundTrip:
    def test_base_state_survives_json(self):
        state = build_r0_state()
        restored = _json_round_trip(state)
        assert restored.model_dump() == state.model_dump()

    def test_generated_scenario_survives_json(self):
        state = generate_scenario(42, "hard")
        restored = _json_round_trip(state)
        assert restored.model_dump() == state.model_dump()

    def test_restored_state_still_advances(self):
        state = generate_scenario(7, "normal")
        restored = _json_round_trip(state)
        decisions = RoundDecision(
            round_num=1,
            products=[ProductDecision(product_name=p.name, price=p.price)
                      for p in restored.get_company("Apex").products],
        )
        result = advance_round(restored, decisions)
        assert result["round_num"] == 1
        assert restored.round_num == 1

    def test_mid_game_snapshot_round_trips(self):
        """A snapshot taken after a couple of rounds must reload identically."""
        state = build_r0_state()
        for _ in range(2):
            decisions = RoundDecision(
                round_num=state.round_num + 1,
                products=[ProductDecision(product_name=p.name)
                          for p in state.get_company("Apex").products],
            )
            advance_round(state, decisions)
        restored = _json_round_trip(state)
        assert restored.model_dump() == state.model_dump()
        assert restored.round_num == 2


class TestRoundDecisionRoundTrip:
    def test_pending_decision_survives_json(self):
        dec = RoundDecision(
            round_num=1,
            products=[ProductDecision(product_name="Atlas", new_pfmn=6.2,
                                      new_size=13.8, price=24.0, production_schedule=1700)],
        )
        restored = _json_round_trip(dec)
        assert restored.model_dump() == dec.model_dump()

    def test_empty_pending_is_none_safe(self):
        # pending_json may be null in the DB; validate must accept a minimal decision.
        dec = RoundDecision(round_num=1, products=[])
        restored = _json_round_trip(dec)
        assert restored.round_num == 1
        assert restored.products == []


class TestSaasModulesImportSafe:
    def test_import_without_supabase(self):
        import sim.auth as auth
        import sim.billing as billing
        import sim.db  # noqa: F401  (importing must not require supabase)
        # Local-mode fast paths must never touch supabase or session_state.
        assert auth.auth_enabled() is False
        assert billing.has_full_access() is True
        assert billing.can_advance(3) == (True, "")
        assert billing.can_create_game(99) is True
