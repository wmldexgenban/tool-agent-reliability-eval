# Architecture

## Config

`agent_eval.config` validates YAML into `ExperimentConfig`, `EnvironmentConfig`, `ModelConfig`, and `RetryConfig`. The configuration selects environment fields, evidence availability, models, policies, concurrency, and output locations.

## Environment

`InventoryEnvironment` emits stock records with a potentially stale recommendation. `TicketingEnvironment` emits support tickets with priority scores and a potentially weak routing hint. Both return `ToolObservation`, including task text, visible response, ground truth, and evidence catalog.

## Provider

`ModelProvider.generate` is the async boundary. `MockProvider` is deterministic and needs no credentials. `OpenAICompatibleProvider` sends JSON-mode chat requests to a configured endpoint and preserves usage only when the endpoint returns it.

## Runner

`ExperimentRunner` expands model × policy × case into episode jobs. `ConcurrencyLimiter` bounds active work. `with_retry` retries timeouts and provider 429/5xx failures with exponential backoff. Each completed episode is appended to JSONL and indexed in SQLite before the batch continues.

## Agent and policy

`ToolUsingAgent` builds the prompt and parses a `CandidateAnswer`. Policies then decide whether the candidate can become a final submission. `BaselinePolicy` accepts the candidate, `SelfCheckPolicy` changes the prompt only, and `EvidenceGuard` uses an `EvidenceRequirementRegistry` with named validators.

## Trace and storage

`TraceRecorder` emits `TASK_CREATED`, `TOOL_RESPONSE_RECEIVED`, `CANDIDATE_SELECTED`, `EVIDENCE_CHECKED`, `SUBMISSION_ACCEPTED` or `SUBMISSION_REJECTED`, and `EPISODE_EVALUATED`. `attribute_failure` adds a structured `failure_stage` such as `candidate_selection`, `evidence_validation`, or `submission`; it never stores hidden model reasoning. The complete trace travels with the episode result in JSONL. SQLite stores only completion state for lightweight resume checks. A compact public example is written to `reports/example_trace.json`.

## Evaluator

Correctness checks accepted final values against ground truth. Reliability classification independently checks evidence validity, unsupported commits, guard rejections, and false rejections. `aggregate_outcomes` groups episodes by model and policy, while `render_report` produces the comparison Markdown.
