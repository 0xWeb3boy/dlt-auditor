# Validation Card

## Metadata

- ID: `heimdall-v2-2025-05-08-heimdall-v2-transaction-processing-6f86ef9b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-continuity-validation`

## What Confirmed The Issue

- Evidence 1: both message-server and side-tx checkpoint paths enforce exact successor start block after the patch.
- Evidence 2: buffer retrieval errors are logged and returned instead of allowing later existence logic to proceed.

## What Could Have Invalidated It

- Compensating control 1: every externally reachable checkpoint path already performed exact continuity before this code.
- Compensating control 2: buffer read errors are impossible or represented separately from ordinary missing-buffer state.

## Severity Guidance

- Expected impact band: checkpoint-integrity / state-integrity hardening.
- Expected severity band: medium.

## False-Positive Cautions

- Caution 1: similar duplicate-path fixes may be defense in depth if only one path is externally reachable.
- Caution 2: avoid escalating to high severity without attacker control over checkpoint range acceptance.
