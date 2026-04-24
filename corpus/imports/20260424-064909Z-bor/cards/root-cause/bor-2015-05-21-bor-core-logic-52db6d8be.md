# Root-Cause Card

## Metadata

- ID: `bor-2015-05-21-bor-core-logic-52db6d8be`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verification-bypass`
- Confidence tier: `tier_a_confirmed`

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

- Primary impact: sync-integrity-bypass
- Secondary impact: high severity conditions

## Short Reusable Lesson

- The cross-check state was too weak: it remembered only expiration and later accepted any queued parent for a sampled block hash. That allowed the deferred verification step to test local membership rather than exact ancestry for the sampled block.
