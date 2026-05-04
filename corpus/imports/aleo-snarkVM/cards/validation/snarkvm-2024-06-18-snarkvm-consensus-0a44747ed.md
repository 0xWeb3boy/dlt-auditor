# Validation Card

## Metadata

- ID: `snarkvm-2024-06-18-snarkvm-consensus-0a44747ed`
- Bug family: `staking_registry_and_accountability`
- Bug class: `validator-limit-enforcement`

## What Confirmed The Issue

- Validator address extraction moved from transition input to `Output::Future` argument.
- A regression test rejects bonding when the committee is already at `MAX_COMMITTEE_SIZE`.

## What Could Have Invalidated It

- Another mandatory check proves the input and output validator address are identical.
- A lower storage layer refuses insertion once the committee limit is reached.

## Severity Guidance

- Expected impact band: validator_set_integrity
- Expected severity band: high_or_medium

## False-Positive Cautions

- The first input and Future output are guaranteed equal by a separate enforced constraint.
- The path runs only in tests or offline simulation.
