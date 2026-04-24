# Root-Cause Card

## Metadata

- ID: `rippled-2023-09-11-rippled-p2p-networking-f259cc1ab`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-safety-invariant`

## Violated Invariant

- Invariant: Consensus participants must only advance local safety or liveness state from messages that satisfy the current quorum, ordering, timing, and validator-role rules.

## Trust Boundary

- Boundary: remote peer message -> local node networking/resource manager

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: peer session state, fetch scheduling, handshake slots, or local resource accounting

## Impact Pattern

- Primary impact: consensus-safety, consensus-liveness
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The patch changes rippled consensus handling to preserve and use peer proposal information across accepted/catch-up states, acquire transaction sets for proposals tied to other ledger sequences, and prune recent peer positions by ledger sequence.
