# Root-Cause Card

## Metadata

- ID: `oasis-core-2022-12-08-oasis-core-rpc-client-api-52536d293`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `quote-policy-synchronization`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `attestation-policy-synchronization`

## Violated Invariant

- Invariant: If enclave RPC quote verification depends on the key manager's consensus-published SGX quote policy, the runtime must receive and refresh that policy when it changes so verification does not rely on stale local state.

## Trust Boundary

- Boundary: `host->enclave`

## Attack Surface

- Entrypoint type: `rpc-handler`
- Sensitive sink: `attestation acceptance state`

## Impact Pattern

- Primary impact: `stale-security-policy`
- Secondary impact: `attestation-verification-weakening`

## Short Reusable Lesson

- If enclave RPC quote verification depends on the key manager's consensus-published SGX quote policy, the runtime must receive and refresh that policy when it changes so verification does not rely on stale local state. In this pattern, the pre-fix design appears to have lacked an explicit mechanism to keep key-manager quote-policy state synchronized inside the runtime, especially across epoch/redeploy-driven changes. The evidence supports a state-synchronization gap in attestation policy handling more clearly than a proven verification bypass. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
