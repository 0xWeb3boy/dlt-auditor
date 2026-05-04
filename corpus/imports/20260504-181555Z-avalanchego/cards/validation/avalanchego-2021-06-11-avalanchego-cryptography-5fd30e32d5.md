# Validation Card

## Metadata

- ID: `avalanchego-2021-06-11-avalanchego-cryptography-5fd30e32d5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-canonicalization-mismatch`

## What Confirmed The Issue

- Evidence: Commit subject says "Fix signature verification for proposer blocks".
- Evidence: Signing changed from exported Signature to internal signature before hashing proposer block bytes.
- Evidence: Signing key source changed to the staking certificate private key with crypto.Signer validation.

## What Could Have Invalidated It

- Compensating control: No full Verify implementation is provided.
- Compensating control: No failing test or before-state verification bypass is shown.
- Compensating control: No evidence of forged-block acceptance, replay, funds loss, or chain halt is provided.

## Severity Guidance

- Expected impact band: medium_high_integrity
- Expected severity band: medium_or_low
- Severity rationale: A canonicalization mismatch in a consensus signature path can undermine block authentication, but this record is likely hardening because no concrete forged-block exploit is shown.

## False-Positive Cautions

- Caution: Classify as security hardening for consensus block authentication, not as a proven exploitable security fix.
- Caution: Do not claim state corruption from the supplied evidence.
- Caution: Do not claim private key compromise, double spend, funds loss, or chain halt.
