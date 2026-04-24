# Validation Card

## Metadata

- ID: `bor-2023-07-04-bor-storage-0f9d7d61c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-input-validation`

## What Confirmed The Issue

- TxPool.demoteUnexecutables() now removes conditional transactions whose KnownAccounts validation fails.
- FilterTxConditional applies validation to transaction options during txpool maintenance, tightening acceptance of untrusted pending transactions.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No proof that an external peer could reliably trigger the missing-trie case before this patch.
- No crash report, panic trace, or explicit denial-of-service statement in the commit metadata.
