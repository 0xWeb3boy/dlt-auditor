# Validation Card

## Metadata

- ID: `bor-2015-05-15-bor-core-logic-5c1a7b965`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-peer-chain-validation`

## What Confirmed The Issue

- Live code adds a parent-continuity check before deleting an entry from d.checks.
- Failure path now returns ErrCrossCheckFailed when a checked block's parent is missing from the queue.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No production-path evidence shows what concrete impact the old behavior enabled beyond downloader acceptance logic.
- The diff does not demonstrate consensus compromise, chain acceptance, or permanent state corruption.
