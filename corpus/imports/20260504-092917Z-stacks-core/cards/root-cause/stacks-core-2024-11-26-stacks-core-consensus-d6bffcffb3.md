# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-11-26-stacks-core-consensus-d6bffcffb3`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-state-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fresh-state-lifecycle-binding`

## Violated Invariant

- Invariant: Consensus and validation decisions must use state from the current fork, reward cycle, and lifecycle epoch, not cached or prior-cycle data.

## Trust Boundary

- Boundary: Fork-choice, signer, or chain-tip data crosses into consensus validation.

## Attack Surface

- Entrypoint type: `consensus_state_transition`
- Sensitive sink: canonical tip, fork choice, signer set, or block validation decision

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- The patch changes signer post-validation behavior so a successful block validation response is rechecked against current signer DB state, using a new helper that selects the highest locally or globally accepted signer block. This is plausibly consensus-relevant correctness or hardening work, but the provided evidence does not prove a concrete vulnerability, exploit path, or security impact.
