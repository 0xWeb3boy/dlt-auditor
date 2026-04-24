# Validation Card

## Metadata

- ID: `heimdall-v2-2024-06-24-heimdall-v2-rpc-client-api-316e7e65`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-id-reuse-guard`

## What Confirmed The Issue

- Evidence 1: the validator join path changed from using `GetSignerFromValidatorID` error behavior to direct `DoValIdExist` key-presence testing.
- Evidence 2: the affected state is a validator ID to signer mapping used during staking registration.

## What Could Have Invalidated It

- Compensating control 1: a prior canonical uniqueness constraint rejects duplicate validator IDs before this handler.
- Compensating control 2: the old getter's error semantics were intentionally inverted and documented as "exists" rather than "missing" or read failure.

## Severity Guidance

- Expected impact band: state-integrity / validator-registration-integrity.
- Expected severity band: medium.

## False-Positive Cautions

- Caution 1: do not claim validator takeover or fund loss without an end-to-end path.
- Caution 2: test-only changes to ACK counts are not independent security evidence.
