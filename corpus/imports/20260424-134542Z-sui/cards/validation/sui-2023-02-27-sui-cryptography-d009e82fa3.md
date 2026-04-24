# Validation Card

## Metadata

- ID: `sui-2023-02-27-sui-cryptography-d009e82fa3`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-domain-separation`

## What Confirmed The Issue

- Authority signature APIs changed from raw Signable payloads to IntentMessage<T>-based secure signing and verification.
- VerificationObligation::add_message now requires an explicit Intent and serializes IntentMessage before verification.
- The commit body states authority signatures now commit to intent scope for sender transactions, transaction effects, and checkpoint summaries.
- The affected code is cryptographic authority signature construction and verification in validator/consensus-related paths.

## What Could Have Invalidated It

- No demonstrated exploit path against the previous signature format.
- No proof that two distinct message scopes could share valid signed bytes in practice.
- No evidence of an observed replay, forgery, or consensus safety violation.
- No evidence that excluded proof-of-possession or Narwhal signing headers were fixed here.

## Severity Guidance

- Expected impact band: signature-domain-confusion
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Classify as domain-separation hardening, not a confirmed vulnerability fix.
- Do not claim a concrete request forgery or replay impact from the patch alone.
- Do not claim this fixed all signature domain-separation issues in the project.
- Do not include proof-of-possession or Narwhal header signing in the validated finding.
