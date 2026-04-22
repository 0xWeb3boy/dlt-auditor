# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-06-03-oasis-core-rpc-client-api-3f0716ecd`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `non-production-credential-acceptance`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `credential-policy-gating`

## Violated Invariant

- Invariant: When test keys are disallowed, public keys explicitly designated as test-only must not pass the shared signature verification path, even if the signature is otherwise valid.

## Trust Boundary

- Boundary: `remote-peer->rpc-verifier`

## Attack Surface

- Entrypoint type: `rpc-handler`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `policy-bypass`
- Secondary impact: `none`

## Short Reusable Lesson

- When test keys are disallowed, public keys explicitly designated as test-only must not pass the shared signature verification path, even if the signature is otherwise valid. In this pattern, the shared verifier treated structurally valid keys with correct signatures as acceptable without a separate policy check for designated test-only keys. That meant acceptance depended only on cryptographic validity, not on whether a key was meant for non-production use. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
