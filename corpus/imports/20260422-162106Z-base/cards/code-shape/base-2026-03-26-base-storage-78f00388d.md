# Code-Shape Card

## Metadata

- ID: `base-2026-03-26-base-storage-78f00388d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: Missing read-compare-write validation in the EIP-8130 nonce update path: the handler trusted transaction-supplied `nonce_sequence` enough to derive and write the next stored value without first checking the authoritative stored sequence for that slot. The gas change is a separate accounting correction, not the root cause of the nonce issue.

## Search Motifs

- Motif 1: externally supplied structured data is accepted after only partial validation
- Motif 2: one representation is checked while a different reconstructed or cached representation reaches the sink
- Motif 3: exact consumption, identity binding, or state-coordinate consistency is not rechecked before execution

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed some validation or normalization up front, but a later reuse, reconstruction, or alternate branch could still reach the sink without the exact same property being enforced.

## Patch Pattern

- What the fix changed structurally: Replace a blind state update driven by transaction input with a stateful read-compare-write check against the authoritative storage slot immediately before mutation. Keep gas estimation conservative before execution, then reconcile warm/cold costs once execution context is available.

## False Match Warnings

- What looks similar but is often not a bug: Supported claim: this commit adds missing stateful nonce validation immediately before updating a nonce slot.
