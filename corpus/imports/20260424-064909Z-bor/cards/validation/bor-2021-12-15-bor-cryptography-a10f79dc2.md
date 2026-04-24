# Validation Card

## Metadata

- ID: `bor-2021-12-15-bor-cryptography-a10f79dc2`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `insufficient-signature-coverage`

## What Confirmed The Issue

- SealHash now takes Bor config and becomes fork-aware.
- ecrecover switches to SealHash(header, c) in the signer recovery path.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No proof that an attacker could exploit the omission in practice.
- No evidence of accepted invalid blocks, forged signatures, or a real incident.
