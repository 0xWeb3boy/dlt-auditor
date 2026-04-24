# Validation Card

## Metadata

- ID: `bor-2026-02-26-bor-cryptography-b69ad46c1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `timestamp-validation`

## What Confirmed The Issue

- Adds a new consensus-side upper bound: reject headers with header.Time greater than now plus 30 seconds.
- Change is in verifyHeader, a consensus-critical boundary for validator-controlled block metadata.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No supplied diff for Prepare or other downstream code to independently prove the claimed long sleep or permanent halt.
- No evidence showing real-world exploit conditions, affected versions, or whether all nodes would halt the same way.
