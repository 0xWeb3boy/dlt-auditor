# Validation Card

## Metadata

- ID: `movement-2024-10-02-movement-transaction-processing-3bf63c914`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sequence-number-reuse`

## What Confirmed The Issue

- The commit explicitly states that used sequence numbers prevented an exploit.
- submit_transaction now calls has_invalid_sequence_number and returns an invalid status before continuing.
- The new helper consults used_sequence_number_pool before validating against checkpoint state.

## What Could Have Invalidated It

- A separate pre-existing reservation check guarantees uniqueness before TransactionPipe receives the transaction.
- The used-sequence pool is never populated on the real acceptance path.
- Duplicate accepted transactions are deterministically dropped before any forwarding or execution cost.

## Severity Guidance

- Expected impact band: integrity_or_replay_hardening
- Expected severity band: medium_or_low
- Rationale: Likely security fix in a replay-sensitive admission path, but the preserved evidence does not prove consensus failure, theft, or an end-to-end exploit.

## False-Positive Cautions

- Do not flag if another path atomically reserves sender sequence numbers before this check.
- Do not claim confirmed exploitability without insertion behavior, tests, or an advisory.
