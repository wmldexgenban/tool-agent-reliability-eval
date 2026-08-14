import asyncio

from agent_eval.agents.baseline import ToolUsingAgent
from agent_eval.environments.inventory import InventoryEnvironment
from agent_eval.models.mock_provider import MockProvider
from agent_eval.policies.evidence_guard import EvidenceGuard
from agent_eval.policies.self_check import SelfCheckPolicy
from agent_eval.runner.episode import run_episode


def test_trace_has_ordered_agent_lifecycle() -> None:
    case = InventoryEnvironment().generate_cases(1, 9)[0]
    policy = SelfCheckPolicy()
    outcome = asyncio.run(
        run_episode(
            episode_id="trace-1",
            model_name="mock",
            observation=case,
            agent=ToolUsingAgent(MockProvider(), policy.name, policy.instruction),
            policy=policy,
        )
    )
    assert outcome.status == "completed"
    assert [event.event_type for event in outcome.trace.events] == [
        "TASK_CREATED",
        "TOOL_RESPONSE_RECEIVED",
        "CANDIDATE_SELECTED",
        "EVIDENCE_CHECKED",
        "SUBMISSION_ACCEPTED",
        "EPISODE_EVALUATED",
    ]


def test_trace_attributes_unsupported_candidate_selection() -> None:
    case = InventoryEnvironment().generate_cases(1, 17, evidence_availability="full")[0]
    policy = EvidenceGuard()
    outcome = asyncio.run(
        run_episode(
            episode_id="trace-attribution-1",
            model_name="mock",
            observation=case,
            agent=ToolUsingAgent(MockProvider(), "baseline", "submit the first candidate"),
            policy=policy,
        )
    )
    assert outcome.candidate is not None
    assert outcome.candidate.value != case.ground_truth
    assert outcome.policy_result.accepted is False
    assert outcome.failure_stage == "candidate_selection"
    assert outcome.evaluation["failure_stage"] == "candidate_selection"
    assert outcome.trace.events[-1].data["evaluation"]["failure_stage"] == "candidate_selection"
