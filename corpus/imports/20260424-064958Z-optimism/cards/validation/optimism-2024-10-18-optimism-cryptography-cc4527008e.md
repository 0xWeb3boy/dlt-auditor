# Validation Card

## Metadata

- ID: `optimism-2024-10-18-optimism-cryptography-cc4527008e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation-hardening`

## What Confirmed The Issue

- HazardSafeFrontierChecks now uses CandidateCrossSafe(...) instead of directly trusting LocalDerivedFrom(...) when cross-safe scope is not yet known.
- The patched path rejects mismatches with an explicit conflict when the candidate block at that height is not the expected hazard block.
- CandidateCrossSafe is documented to surface ErrConflict for inconsistency between local-safe and cross-safe DB state.
- New DB helpers (First, FirstAfter) add explicit identity checks before returning or advancing through derivation state.

## What Could Have Invalidated It

- No proof that the old behavior allowed attacker-controlled invalid blocks, logs, or messages to be accepted.
- No exploit scenario, incident report, CVE, or test demonstrating real security impact before the patch.
- Only partial diffs are shown; the full CandidateCrossSafe logic and call graph are not provided.
- No evidence of confidentiality or availability impact; the visible effect is stricter integrity checking.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: low_or_informational

## False-Positive Cautions

- No proof that the old behavior allowed attacker-controlled invalid blocks, logs, or messages to be accepted.
- No exploit scenario, incident report, CVE, or test demonstrating real security impact before the patch.
- Only partial diffs are shown; the full CandidateCrossSafe logic and call graph are not provided.
