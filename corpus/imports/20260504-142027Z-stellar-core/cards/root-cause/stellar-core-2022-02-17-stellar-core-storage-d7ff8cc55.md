# Root-Cause Card

## Metadata

- ID: `stellar-core-2022-02-17-stellar-core-storage-d7ff8cc55`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-overlay-flow-control-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `p2p-flow-control-state-enforcement`

## Violated Invariant

- Invariant: A peer should only continue reading or sending flood traffic when negotiated flow-control state says capacity is available and the peer supports the relevant control messages.

## Trust Boundary

- Boundary: remote-overlay-peer -> local-peer-read-and-flood-capacity

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: read scheduling, flood-message sending, and peer protocol state
- Attacker capability: Send overlay messages at high volume.
- Main precondition: Read loops continue without checking per-peer capacity.

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: resource-exhaustion, p2p-protocol-hardening
- Severity guess: medium because Flow-control gaps can be abused for availability pressure, but the validation kept this as hardening because no concrete exploit was demonstrated.

## Short Reusable Lesson

- P2P flow control must be an enforced protocol state machine, not just accounting around reads and sends.
