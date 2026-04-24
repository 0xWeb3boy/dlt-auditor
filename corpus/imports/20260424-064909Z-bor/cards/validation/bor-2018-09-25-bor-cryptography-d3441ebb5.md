# Validation Card

## Metadata

- ID: `bor-2018-09-25-bor-cryptography-d3441ebb5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-trust-boundary-hardening`

## What Confirmed The Issue

- SignTransaction now returns an error on validator warnings when rejectMode is enabled, changing a warning-only path into fail-closed behavior.
- NewSignerAPI wires a rejectMode flag derived from !advancedMode, indicating stricter default behavior outside advanced mode.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: hardening
- Expected severity band: low

## False-Positive Cautions

- No diff is provided for the claimed AES-GCM key/value swap fix, so that cryptographic claim is not validated here.
- No excerpt shows a concrete pre-patch exploit path, attacker-controlled bypass, or signature/replay abuse.
