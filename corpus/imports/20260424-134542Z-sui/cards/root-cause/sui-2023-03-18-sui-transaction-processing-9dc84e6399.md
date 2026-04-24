# Root-Cause Card

## Metadata

- ID: `sui-2023-03-18-sui-transaction-processing-9dc84e6399`
- Bug family: `authz_and_role_gates`
- Bug class: `object-access-authentication-invariant`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A request crossing a trust boundary must prove the required authority before it can influence privileged protocol state.

## Trust Boundary

- Boundary: submitted transaction or validator response -> execution/effects pipeline

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: authorizing object access or privileged state mutation

## Impact Pattern

- Primary impact: unauthorized-object-read
- Secondary impact: context-dependent

## Short Reusable Lesson

- Authorization must be checked at the boundary where authority is consumed, not inferred from caller-controlled fields or earlier best-effort filters. The patch adds debug-only invariant checking for authenticated object access after transaction execution and before effects are produced. This is security-relevant hardening, but the provided evidence does not establish a concrete production vulnerability or production enforcement change.
