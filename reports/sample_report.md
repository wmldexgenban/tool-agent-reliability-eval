# Evaluation Report: sample

This report summarizes synthetic tool-use episodes produced by the configured run.

| Model | Policy | Episodes | Task Accuracy | Unsupported Commit Rate | Guard Rejection Rate | False Rejection Rate | Evidence Coverage | Avg Latency (ms) | Token Usage (p/c/t) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| inventory-demo/deterministic-mock | baseline | 24 | 0.0% | 100.0% | 0.0% | 0.0% | 0.0% | 11.863 | unavailable |
| inventory-demo/deterministic-mock | evidence_guard | 24 | 100.0% | 0.0% | 0.0% | 0.0% | 100.0% | 11.847 | unavailable |
| inventory-demo/deterministic-mock | self_check | 24 | 100.0% | 0.0% | 0.0% | 0.0% | 100.0% | 11.556 | unavailable |
| ticket-demo/deterministic-mock | baseline | 24 | 0.0% | 100.0% | 0.0% | 0.0% | 0.0% | 11.666 | unavailable |
| ticket-demo/deterministic-mock | evidence_guard | 24 | 100.0% | 0.0% | 0.0% | 0.0% | 100.0% | 12.871 | unavailable |
| ticket-demo/deterministic-mock | self_check | 24 | 100.0% | 0.0% | 0.0% | 0.0% | 100.0% | 12.588 | unavailable |

## Reading the trade-off

Accuracy measures useful task completion. Unsupported Commit measures accepted answers without a valid record reference. Guard Rejection and False Rejection show the cost and risk of deterministic evidence checks.

Sample results generated with the built-in deterministic mock provider.
