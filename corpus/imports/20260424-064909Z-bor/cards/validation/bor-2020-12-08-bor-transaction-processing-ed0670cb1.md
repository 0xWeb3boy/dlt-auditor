# Validation Card

## Metadata

- ID: `bor-2020-12-08-bor-transaction-processing-ed0670cb1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection`

## What Confirmed The Issue

- Commit message explicitly cites EIP155 and chain ID as adding security.
- NewTransactorWithChainID is added for chain-aware signing.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No proof of an actual replay exploit or vulnerable deployment is shown.
- No evidence that all old signing paths were removed or blocked.
