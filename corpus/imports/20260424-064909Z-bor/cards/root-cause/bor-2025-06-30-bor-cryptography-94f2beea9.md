# Root-Cause Card

## Metadata

- ID: `bor-2025-06-30-bor-cryptography-94f2beea9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature authorization and domain binding`

## Violated Invariant

- Invariant: Consensus-critical data must satisfy the same validation rules on every node before it can influence state transition, fork choice, rewards, or canonical-chain decisions.

## Trust Boundary

- Boundary: untrusted signed payload to verifier or signer boundary

## Attack Surface

- Entrypoint type: transaction/message signature verification path
- Sensitive sink: signer recovery, authorization, or replay-protection decision

## Impact Pattern

- Primary impact: consensus-integrity-risk
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The evidence shows missing or delayed validation in the stateless snapshot transition path: recovered signers were not explicitly checked in the shown code for validator-set membership and succession before further snapshot processing. The diff also suggests veBlop-specific snapshot handling was intertwined with the generic path. The provided material does not prove whether this caused only sync correctness issues or a broader security failure.
