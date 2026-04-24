# Validation Card

## Metadata

- ID: `bor-2020-05-17-bor-rpc-client-api-868dc81c8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fail-open-error-handling`

## What Confirmed The Issue

- FinalizeAndAssemble changed from logging CommitStates failure and continuing to returning the error, which is a fail-closed change in consensus logic.
- CommitStates now rejects execution before c.config.Sprint, adding an explicit guard on when state-sync commits may occur.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: low

## False-Positive Cautions

- No proof that the old behavior was attacker-triggerable from an external interface.
- No evidence of an actual exploit, chain split, unauthorized state injection, or validator forgery caused by the prior code.
