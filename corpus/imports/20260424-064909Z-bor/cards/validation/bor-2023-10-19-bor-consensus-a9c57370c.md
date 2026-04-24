# Validation Card

## Metadata

- ID: `bor-2023-10-19-bor-consensus-a9c57370c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## What Confirmed The Issue

- ReorgNeeded previously used f.rand.Float64() < 0.5 in an equal-TD/equal-height tie.
- The new logic uses bytes.Compare(current.Hash().Bytes(), extern.Hash().Bytes()) < 0 as a deterministic tie-break.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No proof of an actual consensus split, exploit, or production incident is provided.
- No evidence shows an attacker could reliably trigger the tie condition for security impact.
