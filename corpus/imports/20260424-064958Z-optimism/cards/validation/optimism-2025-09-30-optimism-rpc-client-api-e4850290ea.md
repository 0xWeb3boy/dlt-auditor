# Validation Card

## Metadata

- ID: `optimism-2025-09-30-optimism-rpc-client-api-e4850290ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `race-condition`

## What Confirmed The Issue

- The commit message repeatedly says "proper locking" and "race solved," directly indicating synchronization remediation.
- TryUpdateEngine now acquires e.mu before running forkchoice-update logic.
- TryBackupUnsafeReorg now acquires e.mu before running reorg logic.
- The affected code reads and mutates unsafe/safe/finalized heads, backupUnsafeHead, and forkchoice-update flags.

## What Could Have Invalidated It

- No proof that an attacker can trigger the race from an external interface.
- No reproducer showing invalid forkchoice, chain split, or acceptance of bad state.
- No evidence of confidentiality, authentication, or memory-safety impact.
- No patch text demonstrating an actual exploited bug rather than preventive serialization.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that an attacker can trigger the race from an external interface.
- No reproducer showing invalid forkchoice, chain split, or acceptance of bad state.
- No evidence of confidentiality, authentication, or memory-safety impact.
