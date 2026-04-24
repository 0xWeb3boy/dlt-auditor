# Validation Card

## Metadata

- ID: `optimism-2025-11-12-optimism-core-logic-c0185733a7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `archive-extraction-path-validation`

## What Confirmed The Issue

- Commit metadata explicitly mentions "tar transversal attack protection".
- The untar path check changed from ad hoc inline validation to a dedicated sanitizeTarPath helper.
- The new helper visibly rejects absolute paths during extraction.
- The new helper also rejects traversal-containing paths, tightening confinement of extracted files under the output directory.

## What Could Have Invalidated It

- No concrete exploit or test case shows the prior logic was bypassable.
- The patch does not prove attacker-controlled archives are reachable in a real deployment path.
- The visible hunks do not show whether symlink, hardlink, or other tar-header edge cases were also affected.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: host-filesystem-integrity
- Expected severity band: low_or_informational

## False-Positive Cautions

- No concrete exploit or test case shows the prior logic was bypassable.
- The patch does not prove attacker-controlled archives are reachable in a real deployment path.
- The visible hunks do not show whether symlink, hardlink, or other tar-header edge cases were also affected.
