# Validation Card

## Metadata

- ID: `bor-2021-02-23-bor-transaction-processing-142fbcfd6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-replay-protection-check`

## What Confirmed The Issue

- SubmitTransaction adds a new !tx.Protected() rejection before SendTx.
- The rejection is enabled by default unless UnprotectedAllowed() is true.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: high

## False-Positive Cautions

- No proof of a concrete exploit, incident, or attacker-controlled exposure in default deployments.
- No evidence that consensus validation or peer-to-peer transaction handling was vulnerable.
