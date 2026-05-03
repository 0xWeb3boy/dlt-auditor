# Root-Cause Card

## Metadata

- ID: `firedancer-2025-01-10-firedancer-consensus-63a0855e2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-state-persistence`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `failure-path-nonce-finalization`

## Violated Invariant

- Invariant: Once durable nonce authority checks pass, the runtime must persist the correct nonce-account state on both success and failure paths.

## Trust Boundary

- Boundary: Transaction-driven durable nonce use crossing into persisted account finalization.

## Attack Surface

- Entrypoint type: nonce authorization / transaction finalizer
- Sensitive sink: durable nonce account persistence

## Impact Pattern

- Primary impact: replay protection
- Secondary impact: state integrity

## Short Reusable Lesson

- The runtime validated nonce authority but returned through paths that did not consistently preserve or advance the nonce account state.
