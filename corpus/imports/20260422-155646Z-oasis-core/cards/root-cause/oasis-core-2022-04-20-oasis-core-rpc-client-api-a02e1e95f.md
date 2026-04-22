# Root-Cause Card

## Metadata

- ID: `oasis-core-2022-04-20-oasis-core-rpc-client-api-a02e1e95f`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `improper-trust-verification-gating`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `trust-sync-gating`

## Violated Invariant

- Invariant: When a runtime is configured with a trust root, executor availability/registration should wait until runtime trust sync has completed; generic runtime readiness and last-round availability alone are not sufficient.

## Trust Boundary

- Boundary: `remote-peer->rpc-verifier`

## Attack Surface

- Entrypoint type: `rpc-handler`
- Sensitive sink: `attestation acceptance state`

## Impact Pattern

- Primary impact: `premature-registration`
- Secondary impact: `trust-state-exposure`

## Short Reusable Lesson

- When a runtime is configured with a trust root, executor availability/registration should wait until runtime trust sync has completed; generic runtime readiness and last-round availability alone are not sufficient. In this pattern, the pre-patch executor readiness logic did not gate registration/availability on completion of runtime trust sync, so a runtime could be treated as available before its trust-root synchronization finished. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
