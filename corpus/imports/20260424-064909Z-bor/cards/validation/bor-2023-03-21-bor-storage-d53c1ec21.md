# Validation Card

## Metadata

- ID: `bor-2023-03-21-bor-storage-d53c1ec21`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-set-verification`

## What Confirmed The Issue

- The changed code is in verifyCascadingFields, the header verifier for consensus-critical data.
- The old code retried validator lookup against progressively older ancestors after errors.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No advisory, bug report, or commit message states an exploitable vulnerability.
- The patch does not show whether pre-fix behavior accepted forged/invalid headers or only caused benign verification failures.
