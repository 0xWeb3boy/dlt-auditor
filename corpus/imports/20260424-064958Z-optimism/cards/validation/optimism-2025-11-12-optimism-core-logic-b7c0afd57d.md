# Validation Card

## Metadata

- ID: `optimism-2025-11-12-optimism-core-logic-b7c0afd57d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `archive-path-validation-hardening`

## What Confirmed The Issue

- Commit metadata explicitly mentions tar traversal attack protection.
- Shared untar logic now calls a dedicated sanitizeTarPath helper before writing files.
- New helper explicitly rejects absolute paths.
- Validation still rejects traversal-style path components using ".." checks.

## What Could Have Invalidated It

- No failing pre-patch test or proof of exploit is shown.
- The full sanitizeTarPath implementation is not provided, so complete before/after semantics are not visible.
- The patch evidence does not show whether the old logic allowed escaping the output directory on all supported platforms.
- No evidence is provided for symlink, hardlink, or other tar-header edge cases.

## Severity Guidance

- Expected impact band: host-filesystem-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No failing pre-patch test or proof of exploit is shown.
- The full sanitizeTarPath implementation is not provided, so complete before/after semantics are not visible.
- The patch evidence does not show whether the old logic allowed escaping the output directory on all supported platforms.
