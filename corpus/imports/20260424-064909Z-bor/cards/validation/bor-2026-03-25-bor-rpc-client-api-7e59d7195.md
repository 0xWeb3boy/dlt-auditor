# Validation Card

## Metadata

- ID: `bor-2026-03-25-bor-rpc-client-api-7e59d7195`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-input-nondeterminism`

## What Confirmed The Issue

- The change is in CommitStates, a consensus/state-sync path used by validators.
- The patch adds IsDeterministicStateSync(...) gating and a GetBlockHeightByTime(...) lookup before selecting sync data.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- The excerpt does not show the full post-lookup fetch logic end to end.
- There is no proof of a real-world exploit, attacker primitive, or observed chain split.
