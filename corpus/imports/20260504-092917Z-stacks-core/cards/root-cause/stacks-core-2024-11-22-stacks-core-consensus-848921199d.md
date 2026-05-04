# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-11-22-stacks-core-consensus-848921199d`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-consensus-validation-race`
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
- Secondary impact: fork-choice-divergence

## Short Reusable Lesson

- The patch likely fixes a security-relevant race in signer block validation. The supported claim is that queued validation approval could be applied after the signer's sortition view changed, and the fix rechecks the block against the current view before local acceptance. The evidence does not establish signature forgery, private key compromise, replay, or guaranteed final on-chain invalid block acceptance.
