# Root-Cause Card

## Metadata

- ID: `oasis-core-2023-06-29-oasis-core-rpc-client-api-95923572b`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `state-verification-gap`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `state-verification`

## Violated Invariant

- Invariant: Latest-block post-execution state should not be treated as fully verified until the verifier can check block metadata for that same height through the intended consensus proof path.

## Trust Boundary

- Boundary: `remote-peer->rpc-verifier`

## Attack Surface

- Entrypoint type: `rpc-handler`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `verification-freshness`
- Secondary impact: `integrity-hardening`

## Short Reusable Lesson

- Latest-block post-execution state should not be treated as fully verified until the verifier can check block metadata for that same height through the intended consensus proof path. In this pattern, the verifier stack lacked an explicit end-to-end way to obtain the block metadata transaction, together with the needed proof-bearing transaction data, for the exact height being checked. That left latest-block verification delayed rather than performed through a same-block metadata path. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
