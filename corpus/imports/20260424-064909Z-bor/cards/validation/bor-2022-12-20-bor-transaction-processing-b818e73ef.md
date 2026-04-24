# Validation Card

## Metadata

- ID: `bor-2022-12-20-bor-transaction-processing-b818e73ef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`

## What Confirmed The Issue

- Commit message says validation is made stricter and stops relying on caller-side sanitization.
- Beacon.VerifyHeaders now calls splitHeaders(chain, headers) internally before routing validation.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: high

## False-Positive Cautions

- No proof that malformed headers were previously accepted onto chain rather than only mishandled during validation.
- No demonstrated exploit scenario, network impact, or consensus split caused by the old behavior.
