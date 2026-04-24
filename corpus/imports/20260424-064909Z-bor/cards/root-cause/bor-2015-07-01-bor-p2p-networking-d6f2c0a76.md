# Root-Cause Card

## Metadata

- ID: `bor-2015-07-01-bor-p2p-networking-d6f2c0a76`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource limit and input validity enforcement`

## Violated Invariant

- Invariant: Attacker-controlled input must be bounded and rejected before it can drive unbounded allocation, expensive processing, queue growth, or process termination.

## Trust Boundary

- Boundary: remote peer to node networking boundary

## Attack Surface

- Entrypoint type: inbound p2p message, handshake, or sync response handler
- Sensitive sink: peer table mutation, sync scheduling, or message acceptance

## Impact Pattern

- Primary impact: remote-dos
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The hash fetch loop lacked an explicit bound on pending queued hashes and continued requesting more peer-supplied hashes without checking whether the backlog was already too large.
