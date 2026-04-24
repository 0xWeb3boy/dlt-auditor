# Validation Card

## Metadata

- ID: `bor-2024-05-07-bor-transaction-processing-e4b8058d5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- FeeHistory now rejects rewardPercentiles arrays longer than maxQueryLimit before continuing.
- The new constant maxQueryLimit = 100 introduces an explicit resource-control bound on user-supplied input.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No proof of a previously exploitable crash, hang, or measurable resource exhaustion from the old behavior.
- No evidence that the affected path is remotely reachable without authentication in every deployment.
