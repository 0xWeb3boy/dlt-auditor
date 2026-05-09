# Code-Shape Card

## Metadata

- ID: `solana-2021-06-01-solana-cryptography-b000d490ce`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-mitigation`

## Code Shape Summary

The patch introduces cost-based transaction admission and accounting in Solana's banking stage. It adds CostModel/CostTracker plumbing, filters over-limit transactions into a retryable/unprocessed path, and accounts cost only for processed transactions. The evidence supports resource-management hardening, not a confirmed vulnerability fix, signature-validation fix, or replay fix.

## Search Motifs

- search for resource exhaustion mitigation checks near cryptography entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where stake delegation, withdrawal, reward accounting, vote authority, or validator weight is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Introduce resource-budget admission control before transaction processing, defer over-limit transactions, and update shared budget state only for transactions actually processed.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
