# Root-Cause Card

## Metadata

- ID: `snarkos-2020-04-06-snarkos-cryptography-95e340487`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `merkle-membership-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `merkle-membership-binding`

## Violated Invariant

- Invariant: A proof or ledger update that claims commitment membership must bind the witness path to the same Merkle parameters and root used by ledger state.

## Trust Boundary

- Boundary: `witness/prover->ledger-verifier`

## Attack Surface

- Entrypoint type: `zk-proof-validation-path`
- Sensitive sink: ledger commitment membership and DPC validity constraints
- Attacker capability: construct or influence DPC witness data; submit proof or transaction data relying on commitment membership.
- Preconditions: membership constraints participate in validity; non-dummy commitments should be tied to a ledger Merkle root.

## Impact Pattern

- Primary impact: invalid commitment membership accepted.
- Secondary impact: ledger/proof validity invariant weakened.
- Severity guide: `medium` for `state-integrity` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- A proof or ledger update that claims commitment membership must bind the witness path to the same Merkle parameters and root used by ledger state. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch is best characterized as a DPC Merkle membership fix, not replay or signature validation. The grounded evidence shows ledger setup and construction changing from the underlying CRH parameter type (`P::H`) to the full Merkle parameter type (`P`/`Self::Parameters`), and the inner circuit membership check changing from commented-out code to an active `conditionally_check_membership` call for non-dummy commitments. That is security relevant because Merkle membership is part of the DPC validity invariant, but the evidence does not prove a concrete exploit path or impact. 1. In `dpc/src/ledger/ledger.rs`, the patch replaces `Ok(P::H::setup(rng))` with `Ok(P::setup(rng))`. 2. In `dpc/src/
