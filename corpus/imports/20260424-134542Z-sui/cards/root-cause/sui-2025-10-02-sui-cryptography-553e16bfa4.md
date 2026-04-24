# Root-Cause Card

## Metadata

- ID: `sui-2025-10-02-sui-cryptography-553e16bfa4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Malformed or adversarial inputs must be rejected before they reach parsing, execution, or state-commit logic that assumes well-formed data.

## Trust Boundary

- Boundary: signed payload or certificate bytes -> trust decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: committing security-sensitive protocol state

## Impact Pattern

- Primary impact: availability
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch is best treated as bridge node API input-validation and availability hardening. The strongest evidence is the new `validate_list_size` helper in `server/mod.rs`, whose comment explicitly says it prevents DoS during u8 conversion in encoding.
