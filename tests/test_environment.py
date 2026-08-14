from agent_eval.environments.inventory import InventoryEnvironment
from agent_eval.environments.ticketing import TicketingEnvironment


def test_inventory_ground_truth_is_maximum_visible_quantity() -> None:
    cases = InventoryEnvironment().generate_cases(24, 17, field_naming="strong", evidence_availability="full")
    assert len(cases) == 24
    for case in cases:
        winner = max(case.response["items"], key=lambda item: item["available_stock"])
        assert case.ground_truth == winner["sku"]


def test_ticket_environment_is_reproducible() -> None:
    first = TicketingEnvironment().generate_cases(4, 23)
    second = TicketingEnvironment().generate_cases(4, 23)
    assert [case.model_dump() for case in first] == [case.model_dump() for case in second]

