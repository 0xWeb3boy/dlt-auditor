# Root-Cause Card

## Metadata

- ID: `base-2026-03-26-base-storage-78f00388d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `replay-protection`

## Violated Invariant

- Invariant: If the EIP-8130 handler is the authority that advances a `(sender, nonce_key)` nonce slot, it should only increment that slot when the stored sequence equals the transaction's claimed `nonce_sequence`; otherwise it should reject rather than overwrite state from transaction input alone.

## Trust Boundary

- Boundary: `chain state, checkpoint, or persistent storage input->proposer or validator logic`

## Attack Surface

- Entrypoint type: `checkpoint-or-state-validation`
- Sensitive sink: `persistent nonce or replay-protection state`

## Impact Pattern

- Primary impact: `replay-or-ordering-bypass`
- Secondary impact: `state-integrity`

## Short Reusable Lesson

- If the EIP-8130 handler is the authority that advances a `(sender, nonce_key)` nonce slot, it should only increment that slot when the stored sequence equals the transaction's claimed `nonce_sequence`; otherwise it should reject rather than overwrite state from transaction input alone. Missing read-compare-write validation in the EIP-8130 nonce update path: the handler trusted transaction-supplied `nonce_sequence` enough to derive and write the next stored value without first checking the authoritative stored sequence for that slot. The gas change is a separate accounting correction, not the root cause of the nonce issue. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
