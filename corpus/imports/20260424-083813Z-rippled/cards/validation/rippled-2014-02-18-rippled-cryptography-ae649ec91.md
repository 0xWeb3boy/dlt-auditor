# Validation Card

## Metadata

- ID: `rippled-2014-02-18-rippled-cryptography-ae649ec91`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-canonicalization-hardening`

## What Confirmed The Issue

- Evidence 1: SerializedTransaction::checkSign now derives ECDSA::strict from tfFullyCanonicalSig and passes it to accountPublicVerify.
- Evidence 2: RippleAddress verification APIs are changed to propagate an explicit canonicality mode.

## What Could Have Invalidated It

- Compensating control 1: No concrete exploit path is shown.
- Compensating control 2: No evidence that invalid signatures could previously authorize transactions.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: transaction-malleability-reduction
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No concrete exploit path is shown.
- Caution 2: No evidence that invalid signatures could previously authorize transactions.
