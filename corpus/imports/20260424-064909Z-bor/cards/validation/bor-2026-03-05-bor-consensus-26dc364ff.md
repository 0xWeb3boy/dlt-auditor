# Validation Card

## Metadata

- ID: `bor-2026-03-05-bor-consensus-26dc364ff`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## What Confirmed The Issue

- GetVoteOnHash now rejects endBlockNr values that would overflow when adding the confirmation offset.
- The same path now treats a nil confirmation block as invalid instead of only checking for an error.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No proof that an external attacker can supply the oversized values through a reachable interface.
- No evidence of a demonstrated exploit, chain split, or finalized-state violation.
