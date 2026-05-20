# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-bridge-reverted-message-32965`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `reverted-transaction-withdrawal-message-inclusion`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `state-transition-result-gating`

## Violated Invariant

- Only successfully executed transactions may contribute withdrawal or message identifiers to committed bridge execution data.

## Trust Boundary

- Boundary: `vm-receipt->block-execution-data`
- Entrypoint type: `state-transition`
- Sensitive sink: `message id commitment used for L1 withdrawal proofs`

## Attack Surface

- Submit an L2 transaction that emits a withdrawal message and then intentionally reverts.
- Relay or query the committed message proof after the failed transaction is included.

## Exploit Preconditions

- Execution data aggregates MessageOut receipt ids before checking the final transaction status.
- The bridge proof path trusts committed message ids without rechecking transaction success.

## Impact Pattern

- Primary impact: `asset-integrity`
- Secondary impact: `unauthorized-withdrawal`
- Blast radius: `cross-domain`
- Severity guess: `critical`

## Short Reusable Lesson

- Security-bearing execution artifacts must be committed only after the final state-transition result is known.
