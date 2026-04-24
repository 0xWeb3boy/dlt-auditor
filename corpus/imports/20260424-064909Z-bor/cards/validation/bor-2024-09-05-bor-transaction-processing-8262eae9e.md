# Validation Card

## Metadata

- ID: `bor-2024-09-05-bor-transaction-processing-8262eae9e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-context-mismatch`

## What Confirmed The Issue

- LastStateId changed from Call(...) to CallWithState(...) and now passes the supplied state.
- The old Call(...) wrapper forwarded nil state, so the explicit state snapshot was not preserved.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No evidence shows how LastStateId influences final validation or consensus decisions upstream.
- No proof of attacker-controlled trigger, exploit path, or real consensus split is provided.
