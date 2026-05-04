# Root-Cause Card

## Metadata

- ID: `fuel-core-2024-07-27-fuel-core-storage-1cfbb05932`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `reverted-transaction-withdrawal-message-inclusion`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `state-transition-result-gating`

## Violated Invariant

- Only successfully executed transactions may contribute withdrawal/message identifiers to committed block execution data.

## Trust Boundary

- Boundary: `vm-receipt->block-execution-data`
- Entrypoint type: `state-transition`
- Sensitive sink: `message id commitment and withdrawal inclusion in block header data`

## Attack Surface

- Submit transactions that emit withdrawal/message receipts and intentionally revert.
- Repeat attempts to create conflicting or duplicate withdrawal artifacts.

## Exploit Preconditions

- Execution data aggregates receipt message ids before or regardless of final transaction status.
- Downstream withdrawal processing trusts committed message ids.

## Impact Pattern

- Primary impact: `asset-integrity`
- Secondary impact: `state-integrity`
- Blast radius: `chain-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Execution artifacts with asset semantics must be gated by final transaction success, not merely by receipt presence.
