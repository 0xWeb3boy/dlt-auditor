# Validation Card

## Metadata

- ID: `bor-2026-01-27-bor-transaction-processing-0850faf21`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-invariant-checks`

## What Confirmed The Issue

- State processing now aborts when receipt count does not match block transaction count after Bor finalization.
- The same invariant check was added to the parallel state processor, indicating deliberate fail-closed protection across execution paths.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No evidence shows an attacker could reliably trigger these inconsistent states through an exposed interface.
- No proof of a real exploit, consensus split, or funds impact is provided in the patch snippets.
