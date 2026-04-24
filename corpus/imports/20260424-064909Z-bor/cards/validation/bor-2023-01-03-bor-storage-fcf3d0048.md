# Validation Card

## Metadata

- ID: `bor-2023-01-03-bor-storage-fcf3d0048`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-validation`

## What Confirmed The Issue

- newFilter is the peer compatibility filter for remote fork IDs, so it sits on an externally influenced validation path.
- The patch separates forksByBlock and forksByTime, removing mixed validation across different transition types.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No commit text or test demonstrates a concrete attack or user-triggerable exploit.
- No evidence shows actual consensus failure, state corruption, privilege gain, or remote crash.
