# Root-Cause Card

## Metadata

- ID: `oasis-core-2022-04-20-oasis-core-rpc-client-api-40afd4203`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `trust-root-verification`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `trust-root-verification`

## Violated Invariant

- Invariant: If a runtime is configured with a trust root, the executor should not register as available until trust synchronization has completed.

## Trust Boundary

- Boundary: `operator->registry`

## Attack Surface

- Entrypoint type: `registration-path`
- Sensitive sink: `runtime registry admission`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- If a runtime is configured with a trust root, the executor should not register as available until trust synchronization has completed. In this pattern, the availability state machine did not include completion of runtime trust synchronization as a prerequisite for registration or advertised availability. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
