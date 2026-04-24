# Validation Card

## Metadata

- ID: `optimism-2025-12-03-optimism-consensus-8924fbe38d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- Adds an explicit guard rejecting batch.epoch_num < l2_safe_head.l1_origin.number in span-batch extraction.
- Adds the same outdated-origin check in check_batch, showing intentional enforcement of a protocol/validator invariant at multiple entry points.
- Introduces a dedicated L1OriginBeforeSafeHead error path for invalid overlapping span batches.
- Changes singular-batch extraction failures to log, flush state, and return temporary NotEnoughData, reducing inconsistent handling in validator flow.

## What Could Have Invalidated It

- No proof of real-world exploitability, attacker control, or production impact is provided.
- No evidence shows a chain split, fund loss, denial of service, or other concrete security consequence.
- The commit message says the older BatchQueue path was still unfinished work marker, so the patch was not yet full subsystem coverage.
- The patch does not include an advisory, CVE, or explicit statement that a security vulnerability was fixed.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof of real-world exploitability, attacker control, or production impact is provided.
- No evidence shows a chain split, fund loss, denial of service, or other concrete security consequence.
- The commit message says the older BatchQueue path was still unfinished work marker, so the patch was not yet full subsystem coverage.
