# Validation Card

## Metadata

- ID: `movement-2024-10-21-movement-transaction-processing-4aae3dcb9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sequence-number-admission`

## What Confirmed The Issue

- submit_transaction moved from inline sequence validation to has_invalid_sequence_number.
- Tests now expect duplicate submissions not to be forwarded again.
- The validation result is handled before the transaction continues through the pipe.

## What Could Have Invalidated It

- A downstream deduplication layer already prevents any observable duplicate forwarding.
- The test change only reflects behavior unrelated to security-sensitive admission.
- The helper does not check local pending state on the actual execution path.

## Severity Guidance

- Expected impact band: integrity_or_replay_hardening
- Expected severity band: medium_or_low
- Rationale: The evidence includes duplicate-submission test expectations and a shared validation helper, but not a proven DoS, consensus break, or economic exploit.

## False-Positive Cautions

- Do not treat every refactor to a helper as security without duplicate or pending-state evidence.
- Do not claim consensus failure when the finding only proves admission hardening.
