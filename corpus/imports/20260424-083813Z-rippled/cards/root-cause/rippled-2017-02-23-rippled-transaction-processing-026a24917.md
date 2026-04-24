# Root-Cause Card

## Metadata

- ID: `rippled-2017-02-23-rippled-transaction-processing-026a24917`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-invariant-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-and-state-invariant-validation`

## Violated Invariant

- Invariant: Untrusted protocol input must satisfy structural, semantic, and state-dependent invariants before it is admitted to ledger, consensus, storage, or trust-management state.

## Trust Boundary

- Boundary: untrusted transaction -> deterministic ledger state transition

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: ledger state, balance/reserve accounting, or transaction authorization outcome

## Impact Pattern

- Primary impact: ledger-integrity, consensus-safety
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The evidence supports that commit 026a24917 adds a transaction invariant-checking framework to rippled, gated by the EnforceInvariants amendment.
