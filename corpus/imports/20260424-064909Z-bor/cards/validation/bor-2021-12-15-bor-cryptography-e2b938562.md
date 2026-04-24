# Validation Card

## Metadata

- ID: `bor-2021-12-15-bor-cryptography-e2b938562`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-mismatch`

## What Confirmed The Issue

- SealHash and ecrecover were updated to take *params.BorConfig, so validator recovery now follows active fork rules.
- encodeSigHeader now conditionally appends header.BaseFee for Jaipur blocks, changing the fields covered by the signed hash.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No proof that an attacker could forge signatures, impersonate validators, or get invalid blocks accepted.
- No concrete evidence of a chain split, finalized safety failure, or remotely triggerable denial of service in the patch itself.
