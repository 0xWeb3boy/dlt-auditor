# Validation Card

## Metadata

- ID: `sui-2022-08-16-sui-cryptography-e65338451c`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `empty-batch-signature-validation`

## What Confirmed The Issue

- Batch verification paths in the generic trait, Ed25519, BLS12-381, and BLS12-377 now reject `sigs.is_empty()`.
- The previous shown logic rejected count mismatches but did not explicitly reject zero signatures where public keys and signatures could both be empty.
- The added error text explicitly identifies empty batches as dangerous and potentially related to bypassing signature verification.
- The changes are in cryptographic verification code and are accompanied by related test updates according to the commit metadata.

## What Could Have Invalidated It

- No higher-level caller or network-facing path is shown accepting attacker-controlled empty batches.
- No proof is shown that empty-batch success caused transaction forgery, replay, or consensus failure.
- No concrete vulnerability advisory, exploit scenario, or security issue reference is supplied.
- The evidence does not establish private-key compromise or cryptographic signature forgery.

## Severity Guidance

- Expected impact band: signature-verification-bypass
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Keep the finding as security hardening, not a proven exploitable security fix.
- Describe the issue as empty-batch signature verification hardening.
- Do not claim replay, request forgery, transaction forgery, or consensus impact from the provided evidence alone.
- Do not claim remote exploitability unless supported by additional caller evidence.
