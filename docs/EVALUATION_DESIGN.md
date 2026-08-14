# Evaluation Design

## Why accuracy is not enough

An agent can be correct for the wrong reason, copy a summary hint that happens to be right, or avoid risk by refusing every task. These behaviors have different product consequences even when a single accuracy number looks similar.

## Evidence-aware submission

Each candidate contains `value`, `answer_type`, `evidence_refs`, and `confidence`. The guard resolves a requirement for the answer type, checks that a reference belongs to the visible response, and verifies that the cited record supports the submitted value. Missing, mismatched, or unknown evidence produces `insufficient_evidence` and blocks final submission.

## Trace-based failure attribution

The evaluator preserves the transition from task creation to tool response, candidate selection, evidence check, submission, and scoring. This distinguishes a bad tool response from a candidate-selection error, a missing evidence link, and a policy rejection. The trace is designed for inspection and future dashboards, not only final aggregate scores.

## Strategy comparison

- `baseline`: measures the unassisted failure surface.
- `self_check`: tests whether a concise verification instruction changes model behavior.
- `evidence_guard`: tests a deterministic post-generation control that can reject unsupported submissions.

The comparison should be read as a product trade-off: more reliable answers may cost extra latency or token usage, while an overly strict guard may create false rejections. The v1 report makes all of those dimensions explicit.

