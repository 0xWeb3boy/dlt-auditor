# Root-Cause Card

## Metadata

- ID: `sui-2023-09-02-sui-cryptography-980b1496e0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `multisig-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-verification`

## Violated Invariant

- Invariant: Malformed or adversarial inputs must be rejected before they reach parsing, execution, or state-commit logic that assumes well-formed data.

## Trust Boundary

- Boundary: signed payload or certificate bytes -> trust decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: committing security-sensitive protocol state

## Impact Pattern

- Primary impact: sdk-cryptographic-integrity-hardening
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch hardens TypeScript SDK multisig handling by adding validation around `MultiSigPublicKey` construction and partial-signature combination.
