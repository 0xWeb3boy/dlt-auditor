# Validation Card

## Metadata

- ID: `oasis-core-2020-01-29-oasis-core-cryptography-f8809788d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- Evidence 1: The patch adds explicit node-role checks for advertised runtime kinds, explicit non-zero group-size checks for compute runtimes, and a second validation phase that uses a built runtime lookup to re-check compute runtime references.
- Evidence 2: The source finding states the invariant explicitly: Registry admission should reject descriptors that are internally malformed or inconsistent with role and runtime-reference constraints before they enter registry or genesis state.

## What Could Have Invalidated It

- Compensating control 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Compensating control 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Caution 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.
