# Code-Shape Card

## Metadata

- ID: `movement-2024-10-21-movement-transaction-processing-4aae3dcb9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sequence-number-admission`

## Code Shape Summary

- An inline committed-state sequence check was replaced by a shared has_invalid_sequence_number helper, and tests were updated so duplicate submissions are not forwarded again. The reusable pattern is centralizing nonce/sequence validation so all admission routes enforce pending-state and committed-state constraints consistently.

## Search Motifs

- inline sequence_number < committed_sequence_number check in submit path
- duplicate transaction test changes from forwarded twice to not forwarded again
- new shared nonce/sequence validation helper used before mempool insertion
- local pending sequence state consulted during admission

## Typical Asymmetry

- One path had a narrow committed-state check while the reusable validity semantics lived elsewhere or did not cover duplicates.

## Patch Pattern

- Replace ad hoc committed-state checks with a shared invalid-sequence helper, invoke it before acceptance, and update regression tests around duplicate submission behavior.

## False Match Warnings

- Do not treat every refactor to a helper as security without duplicate or pending-state evidence.
- Do not claim consensus failure when the finding only proves admission hardening.
- Duplicate signed transaction handling can be benign if downstream deduplication is guaranteed and cheap.
