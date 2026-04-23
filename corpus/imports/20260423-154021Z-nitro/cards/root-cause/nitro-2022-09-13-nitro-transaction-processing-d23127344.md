# Root-Cause Card

## Metadata

- ID: `nitro-2022-09-13-nitro-transaction-processing-d23127344`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-verification-initialization`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fail-closed-verifier-initialization`

## Violated Invariant

- Invariant: A component that relies on signature verification should construct its verifier during initialization and fail startup if that security dependency cannot be built.

## Trust Boundary

- Boundary: `startup configuration->broadcast client or relay initialization`

## Attack Surface

- Entrypoint type: `node-startup-or-configuration`
- Sensitive sink: `starting a consumer that assumes verified feed input`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- A component that relies on signature verification should construct its verifier during initialization and fail startup if that security dependency cannot be built. The supplied evidence supports an API and startup-hardening change around broadcast-feed verifier setup: `BroadcastClient` now builds its own verifier and can fail during construction, and relay startup now propagates those initialization errors. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
