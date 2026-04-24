# Root-Cause Card

## Metadata

- ID: `bor-2015-05-15-bor-core-logic-5c1a7b965`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-peer-chain-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `network peer authenticity and protocol state validation`

## Violated Invariant

- Invariant: Consensus-critical data must satisfy the same validation rules on every node before it can influence state transition, fork choice, rewards, or canonical-chain decisions.

## Trust Boundary

- Boundary: remote peer to node networking boundary

## Attack Surface

- Entrypoint type: inbound p2p message, handshake, or sync response handler
- Sensitive sink: peer table mutation, sync scheduling, or message acceptance

## Impact Pattern

- Primary impact: sync-integrity-risk
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- Cross-check state was advanced based only on receipt of a block with the expected hash, without verifying that the block's parent matched the queued chain state.
