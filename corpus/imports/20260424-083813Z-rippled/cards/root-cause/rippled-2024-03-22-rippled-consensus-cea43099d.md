# Root-Cause Card

## Metadata

- ID: `rippled-2024-03-22-rippled-consensus-cea43099d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-desync-hardening`
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

- Primary impact: consensus-integrity, node-desynchronization
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The patch fixes a consensus timing/desynchronization condition where a peer could declare consensus with no received proposals and close a non-validated ledger.
