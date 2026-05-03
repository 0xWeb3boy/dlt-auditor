# Root-Cause Card

## Metadata

- ID: `firedancer-2024-11-27-firedancer-storage-2bc30f00b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `crypto-precompile-input-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `precompile-point-and-scalar-validation`

## Violated Invariant

- Invariant: Cryptographic precompiles must validate scalar widths, point encodings, and coordinate choices before verification or decompression work.

## Trust Boundary

- Boundary: Instruction-supplied precompile bytes crossing into secp256r1 verification helpers.

## Attack Surface

- Entrypoint type: precompile input parser
- Sensitive sink: scalar deserialization and public-key recovery/verification

## Impact Pattern

- Primary impact: malformed input acceptance
- Secondary impact: signature verification integrity

## Short Reusable Lesson

- The precompile path decoded secp256r1 scalars and compressed keys with weaker format discipline than the verifier contract expected.
