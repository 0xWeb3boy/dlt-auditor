# Validation Card

## Metadata

- ID: `optimism-2025-05-19-optimism-consensus-6cf0b3a613`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-forkchoice-promotion`

## What Confirmed The Issue

- Pre-patch code explicitly set safe and finalized to the new payload during ExecutionLayerNotFinalized.
- Pre-patch recovery path could return safe = finalized = unsafe in find_starting_forkchoice.
- Post-patch startup logic searches backward from unsafe using L1-origin context instead of blindly promoting heads.
- Engine sync completion now goes through reset().await?, centralizing and tightening startup forkchoice initialization.

## What Could Have Invalidated It

- No proof that an attacker could trigger the bad startup state remotely.
- No evidence of observed consensus divergence, chain split, or fund-impacting behavior.
- No full post-patch logic showing exactly how finalized is derived end to end.
- No test or advisory evidence demonstrating exploitability or prior incorrect acceptance of malicious state.

## Severity Guidance

- Expected impact band: host-filesystem-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that an attacker could trigger the bad startup state remotely.
- No evidence of observed consensus divergence, chain split, or fund-impacting behavior.
- No full post-patch logic showing exactly how finalized is derived end to end.
