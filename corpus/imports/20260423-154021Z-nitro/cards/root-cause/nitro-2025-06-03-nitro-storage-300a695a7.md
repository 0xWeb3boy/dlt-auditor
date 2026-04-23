# Root-Cause Card

## Metadata

- ID: `nitro-2025-06-03-nitro-storage-300a695a7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `finality-boundary-handling`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `finalized-state-initialization`

## Violated Invariant

- Invariant: Recovery and initialization should seed delayed-message tracking from finalized parent-chain boundaries, not from merely observed or current heads.

## Trust Boundary

- Boundary: `finalized parent-chain state->MEL startup and recovery logic`

## Attack Surface

- Entrypoint type: `startup-or-state-recovery`
- Sensitive sink: `initializing delayed-message tracking state`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Recovery and initialization should seed delayed-message tracking from finalized parent-chain boundaries, not from merely observed or current heads. The patch changes MEL startup and state-recovery logic to use the finalized parent-chain block when initializing delayed-message tracking. The evidence supports a reorg-resilience fix in message-extraction state handling, but it does not establish a concrete security vulnerability or exploit path. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
