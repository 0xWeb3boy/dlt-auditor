# Validation Card

## Metadata

- ID: `movement-2024-10-04-movement-p2p-networking-cc8857336`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sequence-validation`

## What Confirmed The Issue

- max_sequence_number changed from max(used_sequence_number, committed_sequence_number) + tolerance to committed_sequence_number + tolerance.
- The changed code is TransactionPipe::has_invalid_sequence_number, an admission-time check.
- The finding is supported by gas-DoS-oriented context but remains likely rather than confirmed.

## What Could Have Invalidated It

- There is an independent strict per-account cap for too-new transactions before this code.
- used_sequence_number cannot exceed committed state in practice.
- The old default path is unreachable for externally supplied transactions.

## Severity Guidance

- Expected impact band: availability_hardening
- Expected severity band: medium_or_low
- Rationale: The patch is in a DoS-relevant transaction admission boundary, but the raw evidence does not show the full resource exhaustion path or gas_dos test behavior.

## False-Positive Cautions

- Do not flag if local used_sequence_number is cryptographically or consensus-derived and cannot be influenced by submitted transactions.
- Do not classify as funds loss or signature bypass from this pattern alone.
