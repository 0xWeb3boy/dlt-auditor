# Root-Cause Card

## Metadata

- ID: `rippled-2013-02-26-rippled-consensus-bd3d28c2f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`
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

- Primary impact: consensus-failure
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The patch likely fixes a security-relevant consensus correctness bug: a race during consensus startup could let the node begin consensus with the wrong last closed ledger.
