# Validation Card

## Metadata

- ID: `sui-2023-01-05-sui-consensus-3e5e0566fd`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-user-signature-verification`

## What Confirmed The Issue

- Commit subject says certificate user signatures are verified in consensus.
- Commit body states incorrect user signatures exposed a vulnerability.
- Test evidence mutates cert.tx_signature bytes before serializing certificate messages.
- Malformed certificates are submitted through ConsensusTransaction::new_certificate_message and validate_batch.

## What Could Have Invalidated It

- Actual consensus_validator implementation guard is not shown.
- Final assertion proving corrupted certificates are rejected is not shown in the excerpts.
- No evidence shows replay behavior, direct transaction forgery, fund theft, or execution impact.

## Severity Guidance

- Expected impact band: invalid-certificate-acceptance
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Supported claim: consensus certificate validation failed to reject certificates with incorrect embedded user signatures.
- Do not claim replay based on the supplied evidence.
- Do not claim arbitrary transaction forgery or direct asset loss.
- Treat AsMut and DerefMut additions as test/support mechanics, not the security fix by themselves.
