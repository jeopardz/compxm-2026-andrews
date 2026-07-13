from sim.state_migration import normalize_save_payload, normalize_state_dump


def _legacy_state():
    companies = []
    for initial in "ABCD":
        company_name = f"{initial} Company"
        companies.append({
            "name": company_name,
            "products": [
                {"name": f"{initial} Product {index}", "company": company_name}
                for index in range(1, 5)
            ],
        })
    return {
        "round_num": 1,
        "companies": companies,
        "history": [{"a company_profit": 123.0, "leader": "A Company"}],
    }


def test_normalize_state_uses_company_initial_and_product_order():
    normalized, aliases = normalize_state_dump(_legacy_state())

    assert [company["name"] for company in normalized["companies"]] == [
        "Apex", "Borealis", "Crestline", "Dynamo",
    ]
    assert [product["name"] for product in normalized["companies"][0]["products"]] == [
        "Atlas", "Axiom", "Arc", "Aura",
    ]
    assert normalized["history"] == [{"apex_profit": 123.0, "leader": "Apex"}]
    assert aliases["A Product 1"] == "Atlas"


def test_normalize_save_payload_updates_pending_and_snapshots():
    state = _legacy_state()
    payload = {
        "game_state": state,
        "pending_decisions": {
            "round_num": 2,
            "products": [{"product_name": "A Product 1"}],
        },
        "round_snapshots": {
            "0": {
                "state": state,
                "pending": {
                    "round_num": 1,
                    "products": [{"product_name": "B Product 2"}],
                },
            },
        },
        "board_results": {"0": {"answer": "C Company"}},
    }

    normalized = normalize_save_payload(payload)

    assert normalized["pending_decisions"]["products"][0]["product_name"] == "Atlas"
    assert normalized["round_snapshots"]["0"]["pending"]["products"][0]["product_name"] == "Brio"
    assert normalized["board_results"]["0"]["answer"] == "Crestline"


def test_current_names_are_idempotent():
    state = _legacy_state()
    once, _ = normalize_state_dump(state)
    twice, aliases = normalize_state_dump(once)

    assert twice == once
    assert all(old == new for old, new in aliases.items())
