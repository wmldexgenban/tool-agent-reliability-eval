from agent_eval.agents.baseline import CandidateAnswer
from agent_eval.environments.inventory import InventoryEnvironment
from agent_eval.evaluators.reliability import classify_reliability
from agent_eval.policies.evidence_guard import EvidenceGuard, EvidenceRequirement, EvidenceRequirementRegistry


def test_guard_accepts_matching_visible_record() -> None:
    case = InventoryEnvironment().generate_cases(1, 17)[0]
    candidate = CandidateAnswer(
        value=case.ground_truth,
        answer_type="inventory",
        evidence_refs=[f"inventory:record:{case.ground_truth}"],
    )
    result = EvidenceGuard().validate(candidate, case)
    assert result.accepted is True
    assert result.validated_refs == candidate.evidence_refs


def test_guard_rejects_missing_or_wrong_evidence() -> None:
    case = InventoryEnvironment().generate_cases(1, 17)[0]
    missing = CandidateAnswer(value=case.ground_truth, answer_type="inventory")
    wrong = CandidateAnswer(value=case.ground_truth, answer_type="inventory", evidence_refs=["inventory:summary"])
    assert EvidenceGuard().validate(missing, case).reason == "insufficient_evidence"
    assert EvidenceGuard().validate(wrong, case).accepted is False


def test_false_rejection_metric_can_be_detected_for_bad_policy_configuration() -> None:
    case = InventoryEnvironment().generate_cases(1, 17)[0]
    candidate = CandidateAnswer(
        value=case.ground_truth,
        answer_type="inventory",
        evidence_refs=[f"inventory:record:{case.ground_truth}"],
    )
    registry = EvidenceRequirementRegistry(
        [EvidenceRequirement(answer_type="inventory", required_sources=["ticket_record"], validator="record_match")]
    )
    result = EvidenceGuard(registry).validate(candidate, case)
    assert result.accepted is False
    evaluation = classify_reliability(candidate, case, result, "evidence_guard")
    assert evaluation["false_rejection"] is True
