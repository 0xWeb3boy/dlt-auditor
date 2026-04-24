# Validation Card

## Metadata

- ID: `optimism-2025-11-24-optimism-consensus-1210787f39`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `payload-derivation-filtering`

## What Confirmed The Issue

- The commit message says deposit-only payload derivation was incorrectly filtering non-deposit payloads.
- A new unit test explicitly asserts that as_deposits_only must strip non-deposit transaction types.
- The build task now uses attributes_envelope.attributes instead of attributes_envelope.inner when selecting the timestamp and submitting payload attributes to fork_choice_updated_v2/v3.
- The changed path feeds engine forkchoice/build logic, which is consensus-sensitive in a blockchain node.

## What Could Have Invalidated It

- No proof that an attacker could reliably trigger or exploit the pre-fix behavior.
- No evidence of an observed consensus split, chain halt, or accepted invalid block.
- The core implementation diff for the faulty filter itself is not shown in the provided excerpts.
- No demonstrated fund impact, privilege gain, or unauthorized state transition is provided.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that an attacker could reliably trigger or exploit the pre-fix behavior.
- No evidence of an observed consensus split, chain halt, or accepted invalid block.
- The core implementation diff for the faulty filter itself is not shown in the provided excerpts.
