# Validation Card

## Metadata

- ID: `oasis-core-2019-05-06-oasis-core-cryptography-bf949bbb0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`

## What Confirmed The Issue

- Evidence 1: The scheduler node-list builder was tightened so that unknown runtimes are skipped, TEE hardware classification starts from an invalid default, and TEE capability objects are locally verified with caps.Verify(ts) before their metadata is used.
- Evidence 2: The source finding states the invariant explicitly: When building epoch node lists, the scheduler should only derive runtime and TEE classification from known runtime entries and capability data that passes local verification at the current timestamp; unknown runtimes and invalid or absent TEE capability data should not be treated as normal eligible inputs.

## What Could Have Invalidated It

- Compensating control 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Compensating control 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Caution 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.
