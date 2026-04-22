# Validation Card

## Metadata

- ID: `oasis-core-2019-08-15-oasis-core-cryptography-4c642baa8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`

## What Confirmed The Issue

- Evidence 1: The registry validation function was tightened so a node claiming the validator role must provide non-empty consensus addresses; otherwise registration fails with 'ErrInvalidArgument'. The TLS-related code was also refactored to separate certificate creation from saving, but that change is not supported as the root security mechanism by the provided evidence.
- Evidence 2: The source finding states the invariant explicitly: Node registration validation should reject role declarations that omit mandatory role-specific metadata. In the provided diff, a node claiming the validator role must include at least one consensus address.

## What Could Have Invalidated It

- Compensating control 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Compensating control 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Caution 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.
