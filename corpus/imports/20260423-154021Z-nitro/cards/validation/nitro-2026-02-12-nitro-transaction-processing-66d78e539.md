# Validation Card

## Metadata

- ID: `nitro-2026-02-12-nitro-transaction-processing-66d78e539`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-divergence`

## What Confirmed The Issue

- Evidence 1: The evidence supports a consensus-divergence fix in `ProduceBlockAdvanced` for retryable auto-redeems.
- Evidence 2: Enforce group-level atomicity for consensus-sensitive derived transactions: snapshot before the originating transaction, process derived work tentatively, defer irreversible finalization, and revert the whole group on a redeem-filter failure.

## What Could Have Invalidated It

- Compensating control 1: If every node independently reconstructs and atomically rejects the same group before finalization, similar code may be less severe than it first appears.
- Compensating control 2: If the edge case is impossible under production filters, downgrade similar cases to hardening.

## Severity Guidance

- Expected impact band: `consensus_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: If every node independently reconstructs and atomically rejects the same group before finalization, similar code may be less severe than it first appears.
- Caution 2: Do not claim finalized chain splits without evidence that different nodes can persist different outcomes from the same group.
