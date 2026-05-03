# Code-Shape Card

## Metadata

- ID: `movement-2024-10-04-movement-p2p-networking-cc8857336`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sequence-validation`

## Code Shape Summary

- The too-new sequence-number ceiling used the same max(local used sequence, committed sequence) base as the stale lower bound. The fix separates those sources: local state can raise the stale lower bound, but the future upper bound stays committed_sequence_number plus tolerance.

## Search Motifs

- max_sequence_number derived from max(used_sequence_number, committed_sequence_number)
- future nonce tolerance uses pending/local state instead of committed state
- TOO_NEW_TOLERANCE applied after attacker-influenced default value
- gas DoS regression added near sequence validation

## Typical Asymmetry

- Local pending state is useful for stale lower bounds, but unsafe as the base for a future-sequence upper bound.

## Patch Pattern

- Use local used-sequence state for stale lower-bound checks only, compute the too-new ceiling from committed state plus tolerance, and log the computed bounds for diagnosis.

## False Match Warnings

- Do not flag if local used_sequence_number is cryptographically or consensus-derived and cannot be influenced by submitted transactions.
- Do not classify as funds loss or signature bypass from this pattern alone.
- Large future-nonce queues may be intentional if separately bounded by account and global quotas.
