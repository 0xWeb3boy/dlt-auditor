# Validation Card

## Metadata

- ID: `bor-2025-06-30-bor-cryptography-94f2beea9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-validation`

## What Confirmed The Issue

- Snapshot.apply(...) now returns UnauthorizedSignerError when the recovered signer is not in snap.ValidatorSet.
- Snapshot.apply(...) now requires snap.GetSignerSuccessionNumber(signer) to succeed before continuing snapshot processing.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No full pre-patch function is shown to prove equivalent signer checks were not enforced elsewhere.
- No test, advisory, or commit text demonstrates that invalid headers were previously accepted in practice.
