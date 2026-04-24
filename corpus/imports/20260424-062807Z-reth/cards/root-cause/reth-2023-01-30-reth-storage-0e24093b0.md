# Root-Cause Card

## Metadata

- ID: `reth-2023-01-30-reth-storage-0e24093b0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-state-invariant`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-rule-enforcement`

## Violated Invariant

- Invariant: Once Spurious Dragon state clearing is active, an account with nonce == 0, balance == 0, and no code or only the empty-code hash must be treated as empty and should not be persisted as a live account. Fork-dependent state-transition rules must be applied at the correct block height.

## Trust Boundary

- Boundary: execution/engine state transition -> persistent storage

## Attack Surface

- Entrypoint type: state-storage-update-path
- Sensitive sink: canonical database, trie updates, or state provider output

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: none proven

## Short Reusable Lesson

- Once Spurious Dragon state clearing is active, an account with nonce == 0, balance == 0, and no code or only the empty-code hash must be treated as empty and should not be persisted as a live account. Fork-dependent state-transition rules must be applied at the correct block height.
