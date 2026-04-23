# Root-Cause Card

## Metadata

- ID: `nitro-2025-11-07-nitro-cryptography-4272c4cfa`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-verification-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `explicit-signature-verification-mode`

## Violated Invariant

- Invariant: Security-sensitive RPC and data-streaming paths should reject unsupported signer configurations early and make signature-checking mode explicit for each operating mode.

## Trust Boundary

- Boundary: `operator config or incoming RPC data->DAS client or server verifier selection`

## Attack Surface

- Entrypoint type: `rpc-startup-or-streaming-configuration`
- Sensitive sink: `starting or accepting data under a selected signature-verification mode`

## Impact Pattern

- Primary impact: `defense-in-depth`
- Secondary impact: `none`

## Short Reusable Lesson

- Security-sensitive RPC and data-streaming paths should reject unsupported signer configurations early and make signature-checking mode explicit for each operating mode. The provided evidence supports correctness and hardening changes in the Anytrust DAS RPC/data-streaming path, not a confirmed vulnerability fix. The patch makes nil-signer chunked-store setup fail fast and makes `DisableSignatureChecking=true` use a consistent no-verification path instead of partially wired verifier logic. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
