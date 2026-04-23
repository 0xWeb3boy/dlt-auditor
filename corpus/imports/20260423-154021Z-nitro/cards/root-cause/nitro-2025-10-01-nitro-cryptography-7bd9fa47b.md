# Root-Cause Card

## Metadata

- ID: `nitro-2025-10-01-nitro-cryptography-7bd9fa47b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-payload-integrity-verification`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `payload-commitment-verification`

## Violated Invariant

- Invariant: A DA or RPC server should recompute and verify a payload commitment from received content and protocol metadata before accepting or serving that payload.

## Trust Boundary

- Boundary: `incoming payload and metadata->DA provider or RPC acceptance path`

## Attack Surface

- Entrypoint type: `rpc-or-payload-validation`
- Sensitive sink: `accepting, storing, or serving payload bytes as valid`

## Impact Pattern

- Primary impact: `payload-tampering`
- Secondary impact: `none`

## Short Reusable Lesson

- A DA or RPC server should recompute and verify a payload commitment from received content and protocol metadata before accepting or serving that payload. The patch replaces a noop payload marker and an always-success verifier with a Keccak-based commitment over the payload plus extras, and enables that verifier on the live DA provider server path. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
