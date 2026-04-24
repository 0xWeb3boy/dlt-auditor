# Validation Card

## Metadata

- ID: `bor-2025-05-22-bor-transaction-processing-20ad4f500`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- ValidateTransaction now rejects transactions whose blob count exceeds opts.MaxBlobCount before further processing.
- ValidationOptions gains MaxBlobCount, showing an explicit resource-control policy was added to admission logic.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No proof that pre-patch behavior was exploitable in practice.
- No demonstrated memory, CPU, disk, or network exhaustion trace.
