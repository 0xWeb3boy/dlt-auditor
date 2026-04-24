# Validation Card

## Metadata

- ID: `sui-2021-09-01-sui-transaction-processing-779a646e14`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-canonicalization-hardening`

## What Confirmed The Issue

- Commit subject is explicitly about signature handling: "Use BCS for signature".
- base_types.rs introduces Signable/BcsSignable and comments that BCS generates canonical bytes suitable for hashing and signing.
- messages.rs removes the visible manual Digestible implementation for Transfer and adds impl BcsSignable for Transfer.
- SignedTransferOrder::new signs value.transfer, matching the shown check_signature behavior against self.transfer.

## What Could Have Invalidated It

- No failing verification path or exploit scenario is shown.
- No evidence shows that the old manual digest was ambiguous or practically bypassable.
- No evidence shows invalid signatures were accepted before the patch.
- No evidence supports the original liveness-failure impact claim.

## Severity Guidance

- Expected impact band: cryptographic-integrity
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Classify as canonical-signature serialization hardening only.
- Do not claim a concrete signature forgery, replay vulnerability, or authentication bypass.
- Do not claim liveness or denial-of-service impact from the supplied evidence.
- Client benchmark changes should be treated as supporting alignment evidence, not proof of a production vulnerability.
