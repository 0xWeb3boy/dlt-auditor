# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-07-31-sei-chain-cryptography-1da04435c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `allocation-size-bound`

## Violated Invariant

- Invariant: Peer- or proposal-supplied sizing fields must be bounded before they affect allocations or consensus state machines.

## Trust Boundary

- Boundary: remote consensus proposal or peer state -> local block-part allocation/state

## Attack Surface

- Entrypoint type: consensus-proposal-or-peer-state-handler
- Sensitive sink: allocating PartSet structures or updating proposal part state

## Impact Pattern

- Primary impact: availability
- Secondary impact: resource-exhaustion

## Short Reusable Lesson

- Validate externally supplied consensus sizing fields before they can affect allocation-sized structures or consensus peer/proposal state, and add a lower-level defensive guard for missed callers. Limits resource pressure from oversized block-part counts. Prevents over-limit proposal metadata from entering ProposalBlockParts setup.
