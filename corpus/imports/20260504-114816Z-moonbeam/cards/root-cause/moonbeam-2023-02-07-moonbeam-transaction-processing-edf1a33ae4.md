# Root-Cause Card

## Metadata

- ID: `moonbeam-2023-02-07-moonbeam-transaction-processing-edf1a33ae4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `precompile-call-policy-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `centralized-precompile-call-policy`

## Violated Invariant

- Invariant: Every precompile dispatch path must apply the same call-mode, recursion, and caller-policy checks before entering sensitive runtime logic.

## Trust Boundary

- Boundary: External EVM call context crosses into per-precompile runtime helpers and dispatch.

## Attack Surface

- Entrypoint type: precompile-dispatch-common-checks
- Sensitive sink: precompile call/delegatecall/callcode execution

## Impact Pattern

- Primary impact: policy-bypass
- Secondary impact: unauthorized-action, precompile-boundary-hardening

## Short Reusable Lesson

- Multiple precompile dispatch paths had local delegatecall/callcode checks. The patch routes them through shared common_checks and common policy configuration. Centralize call-mode and recursion policy in shared precompile check infrastructure and invoke it from every dispatch path.
