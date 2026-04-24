# Root-Cause Card

## Metadata

- ID: `rippled-2023-03-20-rippled-transaction-processing-305c9a8d6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `identifier-collision`
- Confidence tier: `tier_a_confirmed`

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

- Primary impact: state-integrity
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- Confirmed protocol security fix for duplicate NFTokenID creation. The provided commit message and changed code show that the old mint and account deletion rules could allow an issuer to burn an NFT, delete and recreate the account, then mint another NFT with matching ID inputs and receive the same NFTokenID.
