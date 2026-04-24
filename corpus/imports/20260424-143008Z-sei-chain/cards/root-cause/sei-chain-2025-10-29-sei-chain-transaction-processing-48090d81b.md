# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-10-29-sei-chain-transaction-processing-48090d81b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-nonce-bookkeeping`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `admission-bound-bookkeeping`

## Violated Invariant

- Invariant: Mempool nonce or ordering side effects must be recorded only at the same boundary where a transaction is actually admitted.

## Trust Boundary

- Boundary: CheckTx transaction candidate -> active/pending mempool state

## Attack Surface

- Entrypoint type: mempool-admission-handler
- Sensitive sink: updating pending nonce tracker used for promotion/block inclusion

## Impact Pattern

- Primary impact: transaction-ordering-integrity
- Secondary impact: protocol-state-integrity

## Short Reusable Lesson

- Move side-effectful nonce bookkeeping to the same acceptance boundary represented by that bookkeeping, instead of inserting early and relying on rollback across later failure paths. Preserves EVM account nonce ordering during mempool promotion. Prevents rejected transactions from leaving nonce state that influences later transaction eligibility.
