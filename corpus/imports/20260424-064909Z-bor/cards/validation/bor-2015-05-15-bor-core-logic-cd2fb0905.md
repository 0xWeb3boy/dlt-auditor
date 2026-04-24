# Validation Card

## Metadata

- ID: `bor-2015-05-15-bor-core-logic-cd2fb0905`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- The affected code processes hash responses from remote peers during synchronization.
- queue.Insert was changed to report how many hashes were actually new, enabling detection of duplicate-only responses.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: high

## False-Positive Cautions

- The patch does not quantify CPU, bandwidth, or memory impact.
- No exploit trace or test case is shown proving end-to-end denial of service.
