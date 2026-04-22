# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-11-27-oasis-core-validator-ops-a74913bae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-debug-configuration`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `unsafe-debug-gating`

## Violated Invariant

- Invariant: The registry CLI should not proceed with entity-signed-node mode unless the operator has explicitly enabled the corresponding unsafe debug acknowledgement.

## Trust Boundary

- Boundary: `operator->admin-api`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `security-misconfiguration`
- Secondary impact: `none`

## Short Reusable Lesson

- The registry CLI should not proceed with entity-signed-node mode unless the operator has explicitly enabled the corresponding unsafe debug acknowledgement. In this pattern, a missing sanity check allowed an unsafe configuration mode to be selected in the entity load/generation path without the explicit debug acknowledgement now required by the patch. The provided evidence does not show whether this was exploitable beyond local operator misconfiguration. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
