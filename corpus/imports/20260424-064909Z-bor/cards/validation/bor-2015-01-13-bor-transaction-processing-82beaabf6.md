# Validation Card

## Metadata

- ID: `bor-2015-01-13-bor-transaction-processing-82beaabf6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-mismatch`

## What Confirmed The Issue

- Commit subject explicitly says "Fixed consensus issue".
- core/state_transition.go changes CREATE code-deposit gas handling in transaction state transition logic.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No protocol spec, advisory, or issue text is provided to prove the intended rule.
- No included test diff or failing regression case demonstrates the bad behavior.
