# Product Overview

## Problem

Structured API responses often contain both detailed records and convenient summary fields. An agent may copy a hint without checking the records that support or contradict it. A successful tool call therefore does not establish a reliable answer.

## Target users

- AI product teams defining quality gates for tool-using features.
- Agent engineering teams investigating execution failures.
- Model evaluation teams comparing prompts, providers, and safety interventions.

## Core workflow

1. Define the task, environment condition, provider, policy, and episode count in YAML.
2. Generate reproducible inventory or ticket observations.
3. Run model calls under a bounded asyncio scheduler.
4. Persist each trace and outcome as soon as it finishes.
5. Validate evidence references and score usefulness, reliability, latency, and usage.
6. Compare policy trade-offs in a Markdown report.

## Functional scope

The v1 scope includes two synthetic enterprise API environments, a deterministic local provider, an OpenAI-compatible adapter, three submission policies, structured candidates, evidence requirements, JSONL traces, SQLite resume state, retries for transient provider failures, and grouped metric reports.

## Metrics

`task_accuracy` measures accepted final answers matching the environment ground truth. `unsupported_commit_rate` measures accepted candidates without valid evidence. `guard_rejection_rate` and `false_rejection_rate` show whether a guard is useful or overly conservative. `evidence_coverage`, latency, and provider-reported token usage make the result operationally interpretable.

## Trade-offs

A stricter policy can reduce unsupported answers while lowering usefulness if it rejects valid evidence. A prompt-only check may improve behavior at extra model latency and usage. The framework keeps these dimensions visible together so a product decision is not reduced to one score.

