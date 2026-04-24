# Validation Card

## Metadata

- ID: `optimism-2025-12-03-optimism-consensus-a52de0ddea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-invariant-enforcement`

## What Confirmed The Issue

- Adds an explicit outdated-origin rejection when extracting singular batches after the safe head.
- Adds the same outdated-origin guard in batch validation, aligning validation and extraction behavior.
- Changes extraction failure handling to warn, flush buffered state, and return temporary backpressure rather than continue with ambiguous span-batch state.
- Introduces a targeted test for overlapped blocks with an outdated origin, showing the risky condition was intentional and relevant.

## What Could Have Invalidated It

- No proof that pre-fix behavior was attacker-triggerable in a deployed setting.
- No direct evidence of concrete exploitation such as invalid block acceptance, chain split, or fund impact.
- Commit text says the older BatchQueue path was still pending, so the fix was not complete across all paths.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that pre-fix behavior was attacker-triggerable in a deployed setting.
- No direct evidence of concrete exploitation such as invalid block acceptance, chain split, or fund impact.
- Commit text says the older BatchQueue path was still pending, so the fix was not complete across all paths.
