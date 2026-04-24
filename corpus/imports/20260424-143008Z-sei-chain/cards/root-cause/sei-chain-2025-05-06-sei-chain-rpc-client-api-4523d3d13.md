# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-05-06-sei-chain-rpc-client-api-4523d3d13`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `check-then-set-race`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `atomic-counter-enforcement`

## Violated Invariant

- Invariant: Per-actor one-per-height or spam-prevention counters must be checked and updated atomically for the same actor key.

## Trust Boundary

- Boundary: concurrent transaction admission -> validator spam-prevention state

## Attack Surface

- Entrypoint type: ante-handler-counter-check
- Sensitive sink: recording per-validator vote or transaction counter

## Impact Pattern

- Primary impact: spam-prevention-bypass
- Secondary impact: validator-invariant-hardening

## Short Reusable Lesson

- Combine split check-then-update enforcement into one keeper method and guard it with a per-validator lock. Protects the one-vote-per-validator-per-height spam-prevention invariant in this code path. Removes a split read/write sequence that could be race-prone if ante handling is concurrent.
