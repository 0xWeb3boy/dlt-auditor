# Validation Card

## Metadata

- ID: `bor-2014-11-12-bor-transaction-processing-60cdb1148`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integrity-check-omission`

## What Confirmed The Issue

- ProcessWithParent now actively compares derived txSha against the block header TxSha and returns an error on mismatch.
- The restored check sits in block-processing code after applying block state changes, which is a security-sensitive consensus/integrity path.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No proof that mismatched transaction roots were previously accepted as valid blocks.
- No attacker model, exploit narrative, or network impact is shown in the supplied material.
