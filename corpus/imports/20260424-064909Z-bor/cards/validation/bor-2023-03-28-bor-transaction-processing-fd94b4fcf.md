# Validation Card

## Metadata

- ID: `bor-2023-03-28-bor-transaction-processing-fd94b4fcf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- A shared helper adds an explicit memoryPadLimit = 1024 * 1024 for padded memory copies.
- memoryObj.slice stops doing ad hoc allocation/copy and now returns helper errors for oversized requests.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No patch excerpt proves these tracer paths are reachable by untrusted remote users in a default deployment.
- The provided hunks do not show the prestateTracer or opcode-validation panic fixes mentioned in the commit message.
