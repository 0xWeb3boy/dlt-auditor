# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-07-24-oasis-core-cryptography-64cb06901`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-signer-authorization`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `signer-authorization`

## Violated Invariant

- Invariant: A compute commitment's 'TxnSchedSig' must not only be cryptographically valid for the signed message; it must also be produced by a member of the active transaction scheduler committee for the relevant round/epoch.

## Trust Boundary

- Boundary: `committee-member->consensus`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `unauthorized-consensus-message-acceptance`
- Secondary impact: `none`

## Short Reusable Lesson

- A compute commitment's 'TxnSchedSig' must not only be cryptographically valid for the signed message; it must also be produced by a member of the active transaction scheduler committee for the relevant round/epoch. In this pattern, compute-commitment admission validated the transaction-scheduler signature's cryptographic correctness but did not verify that the signer belonged to the active transaction scheduler committee. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
