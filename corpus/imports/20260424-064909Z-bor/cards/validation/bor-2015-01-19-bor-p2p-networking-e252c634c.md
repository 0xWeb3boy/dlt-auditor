# Validation Card

## Metadata

- ID: `bor-2015-01-19-bor-p2p-networking-e252c634c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `public-key-validation`

## What Confirmed The Issue

- respondToHandshake now takes raw remote key bytes, decodes them locally, and returns invalid public key on failure.
- The added check is in the responder side of the crypto handshake, before the connection is treated as encrypted/authenticated.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No proof that the prior behavior enabled exploitability rather than a correctness or crash-only issue.
- No evidence of replay, signature bypass, privilege escalation, or confidentiality/integrity impact.
