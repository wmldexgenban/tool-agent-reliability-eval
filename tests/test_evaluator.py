from agent_eval.agents.baseline import CandidateAnswer
from agent_eval.environments.inventory import InventoryEnvironment
from agent_eval.evaluators.aggregate import aggregate_outcomes
from agent_eval.evaluators.reliability import classify_reliability
from agent_eval.policies.self_check import BaselinePolicy


def test_accuracy_and_unsupported_commit_are_distinct() -> None:
    case = InventoryEnvironment().generate_cases(1, 17)[0]
    candidate = CandidateAnswer(
        value=case.response["summary"]["recommended_sku"],
        answer_type="inventory",
        evidence_refs=["inventory:summary"],
    )
    policy_result = BaselinePolicy().validate(candidate, case)
    evaluation = {
        "task_correct": candidate.value == case.ground_truth,
        **classify_reliability(candidate, case, policy_result, "baseline"),
    }
    metrics = aggregate_outcomes(
        [{"model": "mock", "policy": "baseline", "latency_ms": 2.0, "usage": None, "evaluation": evaluation}]
    )
    assert metrics["task_accuracy"] == 0.0
    assert metrics["unsupported_commit_rate"] == 1.0
    assert metrics["evidence_coverage"] == 0.0

