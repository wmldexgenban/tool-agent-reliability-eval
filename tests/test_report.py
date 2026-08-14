from agent_eval.evaluators.aggregate import render_report


def test_deterministic_report_is_explicitly_labeled() -> None:
    report = render_report(
        "sample",
        {},
        "Provider: MockProvider\nPurpose: pipeline validation",
        title="Deterministic Demo Report",
    )
    assert report.startswith("# Deterministic Demo Report")
    assert "Provider: MockProvider" in report
    assert "Purpose: pipeline validation" in report
