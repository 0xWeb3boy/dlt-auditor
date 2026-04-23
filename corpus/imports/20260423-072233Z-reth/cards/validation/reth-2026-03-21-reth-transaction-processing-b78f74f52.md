# Validation Card

## Metadata

- ID: `reth-2026-03-21-reth-transaction-processing-b78f74f52`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass`

## What Confirmed The Issue

- Evidence 1: The patch adds or restores a fail-closed check, state update, or accounting reconstruction in a security-sensitive path.
- Evidence 2: The changed path sits on a trust boundary: Synthetic or segmented payload metadata crossing into the production payload validator and engine-tree post-execution checks.

## What Could Have Invalidated It

- Compensating control 1: Another mandatory validation layer already enforces the same invariant before this code can affect security-sensitive state.
- Compensating control 2: The changed branch is reachable only from trusted tests, offline tooling, or non-production maintenance flows.

## Severity Guidance

- Expected impact band: consensus_integrity_hardening
- Expected severity band: medium

## False-Positive Cautions

- Pure benchmark or replay-only compatibility code is not enough without a production validation path.
- Skipping receipt-derived checks can be legitimate when cumulative receipt fields are structurally non-comparable.
- Do not claim exploitability unless untrusted payloads can reach the special-case branch.
