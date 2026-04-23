# Code-Shape Card

## Metadata

- ID: `nitro-2026-02-12-nitro-transaction-processing-66d78e539`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-divergence`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence supports a consensus-divergence fix in `ProduceBlockAdvanced` for retryable auto-redeems. The patch adds group-level checkpointing around a user transaction and its generated redeems so that if a redeem triggers `state.ErrArbTxFilter`, the whole tentative group is reverted rather than only dropping the redeem.

## Search Motifs

- Motif 1: block builders checkpoint around individual transactions but not their system-generated follow-on work
- Motif 2: derived retries or auto-redeems can fail a filter after the originating transaction has already committed
- Motif 3: later fixes add group-level snapshots and defer irreversible finalization until derived work succeeds

## Typical Asymmetry

- What was checked in one path but missing in another: The block builder treated the user-visible transaction and its system-generated follow-on work as separate accounting units, even though consensus depended on them behaving as one atomic group.

## Patch Pattern

- What the fix changed structurally: Enforce group-level atomicity for consensus-sensitive derived transactions: snapshot before the originating transaction, process derived work tentatively, defer irreversible finalization, and revert the whole group on a redeem-filter failure.

## False Match Warnings

- What looks similar but is often not a bug: If every node independently reconstructs and atomically rejects the same group before finalization, similar code may be less severe than it first appears.
