# Validation Card

## Metadata

- ID: `oasis-core-2019-11-25-oasis-core-cryptography-d123ab1b1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-identity-validation`

## What Confirmed The Issue

- Evidence 1: The fix makes role handling explicit in the registration worker, adds roles to the descriptor before applying the corresponding hook, gates committee-address registration on role requirements, and filters validator consensus addresses so entries with invalid IDs are dropped before address verification.
- Evidence 2: The source finding states the invariant explicitly: Registry descriptors should only advertise addresses that carry valid identities, and optional address fields should only be included for roles that actually require them.

## What Could Have Invalidated It

- Compensating control 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Compensating control 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Caution 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.
