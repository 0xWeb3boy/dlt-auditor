# Root-Cause Card

## Metadata

- ID: `bor-2015-05-14-bor-transaction-processing-a4246c2da`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation`
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

- Primary impact: availability-degradation
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The downloader boundary conflated two different states: an empty queue and a queued block batch whose head did not connect to known local chain state. That hid invalid input/state from the caller instead of surfacing it explicitly.
