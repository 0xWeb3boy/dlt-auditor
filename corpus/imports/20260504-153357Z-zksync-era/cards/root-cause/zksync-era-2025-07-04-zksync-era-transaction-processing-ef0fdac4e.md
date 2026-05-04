# Root-Cause Card

## Metadata

- ID: `zksync-era-2025-07-04-zksync-era-transaction-processing-ef0fdac4e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-format-and-recovery-validation`

## Violated Invariant

- Invariant: Externally supplied proof signatures must be decoded in the expected domain format and recovery failures must reject the request before proof acceptance logic continues.

## Trust Boundary

- Boundary: External TEE proof submitters cross into proof validation and signer recovery.

## Attack Surface

- Entrypoint type: Proof submission API / request processor.
- Sensitive sink: TEE proof acceptance path and recovered signer used for proof validation.

## Impact Pattern

- Primary impact: Malformed proof signatures are rejected explicitly.
- Secondary impact: Reduced panic or unchecked-recovery risk on request-controlled input.

## Short Reusable Lesson

- Use domain-specific signature decoding at proof boundaries, and convert parse or recovery failure into validation errors. Do not let permissive fallback signatures or unchecked recovery sit on request-controlled proof paths.
