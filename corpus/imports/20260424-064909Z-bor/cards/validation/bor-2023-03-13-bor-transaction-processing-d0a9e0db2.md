# Validation Card

## Metadata

- ID: `bor-2023-03-13-bor-transaction-processing-d0a9e0db2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validator-verification`

## What Confirmed The Issue

- Validator-set verification is moved to an end-of-sprint boundary in verifyCascadingFields, indicating correction of a consensus-sensitive check.
- The code now verifies the validator list against the local contract-derived view, which tightens validation of consensus state.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No full diff shows the exact accept/reject behavior before and after the validator comparison.
- No proof that an attacker could previously cause invalid-block acceptance, chain split, or targeted denial of service.
