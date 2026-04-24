# Validation Card

## Metadata

- ID: `bor-2026-02-18-bor-transaction-processing-bff847a3d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- Commit subject states prevention of OOM from unbounded header reads.
- verifyPendingHeaders now derives startBlock from milestoneEndBlock + 1 instead of an implicitly broader range.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No visible hunk shows the claimed numeric cap at default span length + 1.
- No proof that an external peer can force the unbounded read condition remotely.
