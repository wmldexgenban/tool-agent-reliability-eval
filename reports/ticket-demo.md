# Evaluation Report: ticket-demo

This report summarizes synthetic tool-use episodes produced by the configured run.

| Model | Policy | Episodes | Task Accuracy | Unsupported Commit Rate | Guard Rejection Rate | False Rejection Rate | Evidence Coverage | Avg Latency (ms) | Token Usage (p/c/t) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| deterministic-mock | baseline | 24 | 0.0% | 100.0% | 0.0% | 0.0% | 0.0% | 10.758 | unavailable |
| deterministic-mock | evidence_guard | 24 | 100.0% | 0.0% | 0.0% | 0.0% | 100.0% | 11.892 | unavailable |
| deterministic-mock | self_check | 24 | 100.0% | 0.0% | 0.0% | 0.0% | 100.0% | 11.700 | unavailable |

## Reading the trade-off

Accuracy measures useful task completion. Unsupported Commit measures accepted answers without a valid record reference. Guard Rejection and False Rejection show the cost and risk of deterministic evidence checks.

Provider: MockProvider
Purpose: pipeline validation

These values come from the deterministic mock provider and are intended to verify framework behavior, not compare real model quality.
