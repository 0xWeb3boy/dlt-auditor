# Root-Cause Card

## Metadata

- ID: `oasis-core-2024-10-03-oasis-core-cryptography-0d2f546b2`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-session-state`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `session-freshness`

## Violated Invariant

- Invariant: If the allowed remote enclave identity set changes, cached secure RPC sessions should not continue unchanged under the old policy. Request-scoped peer feedback should remain tied to the originating request even when multiple sessions are active.

## Trust Boundary

- Boundary: `host->enclave`

## Attack Surface

- Entrypoint type: `session-setup`
- Sensitive sink: `secure session cache`

## Impact Pattern

- Primary impact: `stale-trust-policy`
- Secondary impact: `session-state-confusion`

## Short Reusable Lesson

- If the allowed remote enclave identity set changes, cached secure RPC sessions should not continue unchanged under the old policy. Request-scoped peer feedback should remain tied to the originating request even when multiple sessions are active. In this pattern, the visible issue is stale or shared session/request state management in the concurrent enclave RPC path. The evidence supports that session state was not explicitly cleared when remote enclave identity policy changed, and that peer feedback previously went through shared queue-based bookkeeping instead of direct request-bound submission. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
