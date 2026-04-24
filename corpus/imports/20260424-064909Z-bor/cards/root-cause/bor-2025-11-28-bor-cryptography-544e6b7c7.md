# Root-Cause Card

## Metadata

- ID: `bor-2025-11-28-bor-cryptography-544e6b7c7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `numeric-truncation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `arithmetic bounds and resource accounting`

## Violated Invariant

- Invariant: Resource and value accounting must use checked arithmetic and type ranges that cannot wrap, truncate, or undercharge attacker-controlled work.

## Trust Boundary

- Boundary: untrusted block, header, transaction, or state data to consensus engine boundary

## Attack Surface

- Entrypoint type: block/header/transaction validation or state-transition path
- Sensitive sink: canonical chain selection, state root commitment, or consensus state mutation

## Impact Pattern

- Primary impact: malformed-input-acceptance
- Secondary impact: low severity conditions

## Short Reusable Lesson

- Canonical width validation for the Difficulty field was inconsistent. verifySeal narrowed big.Int to uint64 before validating representability, while Header.SanityCheck permitted wider values, allowing malformed non-canonical encodings to reach consensus comparison.
