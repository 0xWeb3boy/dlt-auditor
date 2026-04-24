# Validation Card

## Metadata

- ID: `optimism-2025-12-03-optimism-consensus-a8aa4c3839`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-input-validation`

## What Confirmed The Issue

- Adds an explicit L1OriginBeforeSafeHead rejection when batch.epoch_num is older than the safe head's L1 origin.
- Applies the outdated-origin guard in both singular-batch extraction and batch validation paths, indicating an enforced consensus invariant.
- Changes singular-batch extraction failure handling to log, flush internal state, and return temporary NotEnoughData rather than using the prior generic mapping path.
- Adds a test for the overlapped/outdated-origin case, showing the intended invalid-batch rejection behavior.

## What Could Have Invalidated It

- No proof that attacker-controlled input can practically reach this path in deployed conditions.
- No proof of concrete exploit impact such as chain split, finalized-state corruption, or fund loss.
- Commit text says legacy BatchQueue handling was still unfinished work marker, so full exposure and full remediation are not shown.
- No advisory, incident report, or other evidence ties this patch to a disclosed vulnerability.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that attacker-controlled input can practically reach this path in deployed conditions.
- No proof of concrete exploit impact such as chain split, finalized-state corruption, or fund loss.
- Commit text says legacy BatchQueue handling was still unfinished work marker, so full exposure and full remediation are not shown.
