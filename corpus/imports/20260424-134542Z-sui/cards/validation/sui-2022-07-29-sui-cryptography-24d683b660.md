# Validation Card

## Metadata

- ID: `sui-2022-07-29-sui-cryptography-24d683b660`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-malleability`

## What Confirmed The Issue

- Verifier stopped using signature.sig.to_standard() with verify_ecdsa().
- New verifier recovers the public key from the provided recoverable signature and message.
- Verification now succeeds only when the recovered public key bytes match the expected public key.
- Patch comment explicitly says the change is to ensure non-malleability and avoid accepting both recovery-id variants.

## What Could Have Invalidated It

- No demonstrated transaction replay or request-forgery path.
- No evidence that accepted alternate recovery ids crossed a trust boundary in an exploitable way.
- No consensus, authentication bypass, or asset-impact evidence is shown.
- Signer change is comment-only and does not alter behavior.

## Severity Guidance

- Expected impact band: signature-malleability
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Validated scope is limited to secp256k1 recoverable-signature verification.
- The evidence supports non-malleability hardening, not private key compromise or nonce leakage.
- Do not generalize the issue to other signature schemes.
- Do not claim request forgery or replay without additional protocol evidence.
