# Root-Cause Card

## Metadata

- ID: `rippled-2023-08-18-rippled-consensus-e8a7b2a1f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-management`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-safety-invariant`

## Violated Invariant

- Invariant: Consensus participants must only advance local safety or liveness state from messages that satisfy the current quorum, ordering, timing, and validator-role rules.

## Trust Boundary

- Boundary: peer/validator consensus data -> local consensus and ledger-close machinery

## Attack Surface

- Entrypoint type: consensus-message-or-ledger-close-path
- Sensitive sink: ledger close decision, validator set decision, or consensus safety state

## Impact Pattern

- Primary impact: consensus-safety, network-liveness
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The evidence supports a consensus stability and liveness improvement in rippled, centered on accepted-ledger validation, proposal retention, transaction-set acquisition, and ledger-sequenced proposal tracking.
