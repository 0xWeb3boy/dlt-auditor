# Root-Cause Card

## Metadata

- ID: `rippled-2018-10-08-rippled-rpc-client-api-7fe1d4b9c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-site-redirect-retry-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `trust-root-and-freshness-validation`

## Violated Invariant

- Invariant: Externally supplied trust material must be fetched, redirected, cached, and accepted only under the configured trust roots and transport policy.

## Trust Boundary

- Boundary: remote client or configured service endpoint -> local RPC/client trust boundary

## Attack Surface

- Entrypoint type: rpc-or-client-handler
- Sensitive sink: node configuration, downloaded trust material, or externally visible service behavior

## Impact Pattern

- Primary impact: availability-hardening, bounded-network-fetch
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch changes rippled's ValidatorSite fetch path to represent fetch targets as Resource objects, centralize URL parsing and http/https validation, honor redirect-oriented resource state, use per-site refresh intervals, reset redirect counts per cycle, and add explicit retry/redirect limits.
