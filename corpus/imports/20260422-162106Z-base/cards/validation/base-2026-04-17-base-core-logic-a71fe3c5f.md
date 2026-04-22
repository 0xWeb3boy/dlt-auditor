# Validation Card

## Metadata

- ID: `base-2026-04-17-base-core-logic-a71fe3c5f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `policy-enforcement-bypass`

## What Confirmed The Issue

- Evidence 1: Commit body states that `verifier_l1_confs` delayed a wake-up signal but did not bound direct L1 block fetches.
- Evidence 2: Commit body states that a `ConfDepthProvider` now rejects reads beyond `l1_head - conf_depth`, which is a direct enforcement change.

## What Could Have Invalidated It

- Compensating control 1: Supported: a confirmation-depth policy in a consensus-sensitive path was previously ineffective and is now enforced more directly.
- Compensating control 2: Not supported: a proven exploitable vulnerability, theft risk, finalized-state corruption, or demonstrated consensus split.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported: a confirmation-depth policy in a consensus-sensitive path was previously ineffective and is now enforced more directly.
- Caution 2: Not supported: a proven exploitable vulnerability, theft risk, finalized-state corruption, or demonstrated consensus split.
