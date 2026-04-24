# Validation Card

## Metadata

- ID: `bor-2021-04-06-bor-transaction-processing-706683ea7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection-gating`

## What Confirmed The Issue

- ChainId is explicitly documented as the EIP-155 replay-protection chain id.
- The new canonical implementation checks config.IsEIP155(api.b.CurrentBlock().Number()) before returning a value.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No proof that unconditional pre-fork chainId exposure was exploitable in practice.
- No evidence of replay attacks, transaction acceptance flaws, or consensus impact caused by the old behavior.
