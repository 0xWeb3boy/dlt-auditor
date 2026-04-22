# Root-Cause Card

## Metadata

- ID: `oasis-core-2020-06-23-oasis-core-staking-0f89673a0`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-update-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `update-validation`

## Violated Invariant

- Invariant: A registration must not overwrite a previously stored node record without passing the registry's node-update verification, even if the stored record is expired.

## Trust Boundary

- Boundary: `operator->registry`

## Attack Surface

- Entrypoint type: `registration-path`
- Sensitive sink: `node registry admission`

## Impact Pattern

- Primary impact: `unauthorized-state-modification`
- Secondary impact: `integrity-violation`

## Short Reusable Lesson

- A registration must not overwrite a previously stored node record without passing the registry's node-update verification, even if the stored record is expired. In this pattern, the update-verification check was attached to the wrong control-flow condition. The code keyed verification on the non-new, non-expired branch instead of on the existence of a prior stored node record. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
