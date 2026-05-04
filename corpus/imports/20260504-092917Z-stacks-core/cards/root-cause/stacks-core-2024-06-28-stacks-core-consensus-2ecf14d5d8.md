# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-06-28-stacks-core-consensus-2ecf14d5d8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-tip-monotonicity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-consensus-context-validation`

## Violated Invariant

- Invariant: Consensus decisions must validate evidence, fork context, canonical tip monotonicity, and signer sets against the authoritative chain view before accepting results.

## Trust Boundary

- Boundary: Fork-choice, signer, or chain-tip data crosses into consensus validation.

## Attack Surface

- Entrypoint type: `consensus_state_transition`
- Sensitive sink: canonical tip, fork choice, signer set, or block validation decision

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- The patch changes Nakamoto canonical tip handling in the sortition DB so an accepted block only advances the memoized canonical tip when it is higher than the current tip for the same sortition history. This is plausibly important consensus state maintenance, but the provided evidence does not establish an exploitable vulnerability or concrete security impact.
