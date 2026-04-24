# Root-Cause Card

## Metadata

- ID: `rippled-2012-09-01-rippled-cryptography-3bd054748`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-proposal-duplicate-suppression-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `consensus-safety-invariant`

## Violated Invariant

- Invariant: Consensus participants must only advance local safety or liveness state from messages that satisfy the current quorum, ordering, timing, and validator-role rules.

## Trust Boundary

- Boundary: signed object or key material -> local trust and verification decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: accepted signature, signer identity, manifest, or replay-sensitive object

## Impact Pattern

- Primary impact: consensus-message-suppression, denial-of-service
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The patch fixes duplicate suppression in NetworkOPs::recvPropose. Before the change, the preliminary duplicate key used only proposal sequence, current ledger ID, and public key.
