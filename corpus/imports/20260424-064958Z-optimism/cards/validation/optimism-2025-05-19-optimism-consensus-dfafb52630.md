# Validation Card

## Metadata

- ID: `optimism-2025-05-19-optimism-consensus-dfafb52630`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-forkchoice-initialization`

## What Confirmed The Issue

- Old insert-time logic explicitly set safe_block_hash and finalized_block_hash to the current payload hash during an EL sync transition.
- Old sync-start recovery logic could return forkchoice with safe and finalized both equal to current_fc.un_safe.
- New sync-start logic replaces that shortcut with backward traversal from the unsafe head using L1-origin history.
- Sync-complete handling was moved into an explicit reset/startup path instead of piggybacking on unsafe payload insertion.

## What Could Have Invalidated It

- No reproducer, test, or incident demonstrates that the old behavior was exploitable.
- The provided excerpts do not show full end-to-end enforcement of the new safety criterion.
- No evidence shows an actual chain split, finalized-state corruption, or attacker-controlled impact.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: host-filesystem-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No reproducer, test, or incident demonstrates that the old behavior was exploitable.
- The provided excerpts do not show full end-to-end enforcement of the new safety criterion.
- No evidence shows an actual chain split, finalized-state corruption, or attacker-controlled impact.
