# Validation Card

## Metadata

- ID: `optimism-2026-02-09-optimism-transaction-processing-68b81dd5bb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `finalization-boundary-check`

## What Confirmed The Issue

- The implementation now returns ErrRewindOverFinalizedHead when targetBlock.Number is below currentFinalized.Number.
- Before the patch, computeRewindTargets would derive rewind targets without an explicit finalized-boundary check.
- A dedicated regression test adds a "target before finalized" case and expects the new error.
- The changed code is in rewind/control logic for L2 block references, which is consensus-sensitive state-management code.

## What Could Have Invalidated It

- No proof that an attacker or untrusted input could trigger this rewind path.
- No evidence that the old behavior caused consensus divergence, finalized-state rollback, or chain safety failure in practice.
- No direct demonstration of panic, denial of service, or privilege boundary crossing from the pre-patch behavior.
- No caller-level evidence showing how far the bad rewind targets could propagate before being stopped elsewhere.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that an attacker or untrusted input could trigger this rewind path.
- No evidence that the old behavior caused consensus divergence, finalized-state rollback, or chain safety failure in practice.
- No direct demonstration of panic, denial of service, or privilege boundary crossing from the pre-patch behavior.
