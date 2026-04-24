# Validation Card

## Metadata

- ID: `bor-2015-05-14-bor-transaction-processing-a4246c2da`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation`

## What Confirmed The Issue

- TakeBlocks now returns an error when the queued head's parent is not locally known, instead of silently returning no work.
- processBlocks now aborts on that invalid-head error, so malformed or disconnected sync state is no longer treated as benign.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No proof that the prior behavior caused a persistent remote DoS, crash, or consensus failure.
- No evidence of resource exhaustion, memory safety impact, or cryptographic breakage.
