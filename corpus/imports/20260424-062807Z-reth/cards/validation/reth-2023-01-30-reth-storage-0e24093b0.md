# Validation Card

## Metadata

- ID: `reth-2023-01-30-reth-storage-0e24093b0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-state-invariant`

## What Confirmed The Issue

- Adds a canonical Account::is_empty() definition tied to post-Spurious Dragon semantics, including the empty-code-hash case.
- Skips writing newly created empty accounts when state clearing is active in AccountInfoChangeSet::Created.

## What Could Have Invalidated It

- No test, advisory, or commit message explains a concrete security incident or exploit scenario
- No evidence of an observed consensus split, chain rejection, or attacker-triggerable impact is provided

## Severity Guidance

- Expected impact band: state_or_proof_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No test, advisory, or commit message explains a concrete security incident or exploit scenario
- No evidence of an observed consensus split, chain rejection, or attacker-triggerable impact is provided
