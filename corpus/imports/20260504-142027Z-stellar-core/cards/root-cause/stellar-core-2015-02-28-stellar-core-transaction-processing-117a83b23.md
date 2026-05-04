# Root-Cause Card

## Metadata

- ID: `stellar-core-2015-02-28-stellar-core-transaction-processing-117a83b23`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-transaction-sequence-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `sequence-slot-freshness`

## Violated Invariant

- Invariant: A transaction must be applied only if its signer sequence number matches the current ledger sequence state for the exact sequence slot it claims to advance.

## Trust Boundary

- Boundary: signed-transaction-envelope -> account-sequence-ledger-state

## Attack Surface

- Entrypoint type: transaction-apply-path
- Sensitive sink: operation application and account sequence advancement
- Attacker capability: Submit a signed transaction with a stale, future, or wrong-slot sequence value.
- Main precondition: Pre-application validation does not re-check the exact account and sequence-slot pair.

## Impact Pattern

- Primary impact: transaction-replay-resistance
- Secondary impact: state-integrity, consensus-determinism
- Severity guess: medium because Incorrect sequence enforcement can admit transactions that should be rejected and can disturb ordering or replay invariants, but the finding does not prove theft or consensus divergence.

## Short Reusable Lesson

- Freshness and ordering checks must be repeated at the authoritative state transition boundary, not only at gossip or preliminary validation boundaries.
