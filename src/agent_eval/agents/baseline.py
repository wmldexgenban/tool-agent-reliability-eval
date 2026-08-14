"""Thin tool-using agent wrapper with structured candidate parsing."""

from __future__ import annotations

from pydantic import BaseModel, Field

from agent_eval.environments.base import ToolObservation
from agent_eval.models.base import ModelProvider, ModelRequest, ModelResponse


class CandidateAnswer(BaseModel):
    value: str
    answer_type: str
    evidence_refs: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class AgentTurn(BaseModel):
    candidate: CandidateAnswer
    response: ModelResponse


class ToolUsingAgent:
    """Builds a compact request and requires a structured model response."""

    def __init__(self, provider: ModelProvider, policy_name: str, policy_instruction: str) -> None:
        self.provider = provider
        self.policy_name = policy_name
        self.policy_instruction = policy_instruction

    async def act(self, observation: ToolObservation) -> AgentTurn:
        from .prompts import build_user_prompt

        request = ModelRequest(
            system_prompt=(
                "You are a careful operations assistant. Use visible records as the source of truth. "
                "Never invent evidence references."
            ),
            user_prompt=build_user_prompt(
                observation.task,
                observation.response,
                self.policy_name,
                self.policy_instruction,
            ),
            metadata={
                "tool_response": observation.response,
                "environment": observation.answer_type,
                "policy": self.policy_name,
            },
        )
        response = await self.provider.generate(request)
        return AgentTurn(candidate=CandidateAnswer.model_validate_json(response.text), response=response)

