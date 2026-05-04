# Code-Shape Card

## Metadata

- ID: `snarkos-2020-06-12-snarkos-consensus-4f542d627`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-difficulty-validation`

## Code Shape Summary

- Header verification trusts a supplied difficulty target without comparing it to the difficulty computed from parent state and consensus time rules.

## Search Motifs

- header.difficulty_target read without expected comparison
- get_block_difficulty only used by miner, not verifier
- test mutates consensus-derived header field and still verifies

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Recompute expected difficulty inside header verification, add a mismatch error, and cover the rejection path with a regression test.

## False Match Warnings

- If downstream consensus validation repeats the same check, this path may be redundant
- Test-only header constructors are not security sinks
- Difficulty fields that are metadata only do not carry consensus impact
