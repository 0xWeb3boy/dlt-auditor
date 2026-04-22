# Root-Cause Card

## Metadata

- ID: `base-2026-03-13-base-cryptography-d54fbf46f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-integrity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `configuration-integrity`

## Violated Invariant

- Invariant: If this path is security-sensitive, enclave-side proof generation should use deterministic, canonical per-chain parameters for a known chain set and reject unsupported chains rather than relying on loosely supplied configuration.

## Trust Boundary

- Boundary: `proof producer or network peer->verification routine`

## Attack Surface

- Entrypoint type: `proof-or-signature-verification`
- Sensitive sink: `acceptance of a proof, signature, or derived state transition`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- If this path is security-sensitive, enclave-side proof generation should use deterministic, canonical per-chain parameters for a known chain set and reject unsupported chains rather than relying on loosely supplied configuration. At most, the evidence suggests the earlier design used a more flexible configuration path instead of clearly deriving and pinning enclave parameters from canonical per-chain data. The provided material does not prove that this flexibility created an actual vulnerability in production or that untrusted parties could control the old configuration source. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
