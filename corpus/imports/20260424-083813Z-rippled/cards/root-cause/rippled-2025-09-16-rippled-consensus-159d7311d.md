# Root-Cause Card

## Metadata

- ID: `rippled-2025-09-16-rippled-consensus-159d7311d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-ordering-hardening`
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

- Primary impact: transaction-ordering-integrity
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The patch changes CanonicalTXSet::accountKey from a padded AccountID XORed with salt_ to an amendment-gated BLAKE3(account || salt) derivation, and wires the flag from validated consensus rules in RCLConsensus::Adaptor::doAccept.
