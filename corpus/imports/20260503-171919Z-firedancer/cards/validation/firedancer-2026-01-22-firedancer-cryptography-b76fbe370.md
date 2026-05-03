# Validation Card

## Metadata

- ID: `firedancer-2026-01-22-firedancer-cryptography-b76fbe370`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-poh-validation`

## What Confirmed The Issue

- Evidence 1: Block completion now calls verify_ticks(block) before emitting the normal block-end task.
- Evidence 2: Failed tick verification calls handle_bad_block and emits FD_SCHED_TT_MARK_DEAD instead of completing the block normally.

## What Could Have Invalidated It

- Compensating control 1: No concrete exploit path or attacker-controlled input flow is shown.
- Compensating control 2: No proof that invalid PoH or tick structure previously reached finalized consensus state is supplied.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No concrete exploit path or attacker-controlled input flow is shown.
- Caution 2: No proof that invalid PoH or tick structure previously reached finalized consensus state is supplied.
