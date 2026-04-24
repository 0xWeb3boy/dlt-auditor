# Validation Card

## Metadata

- ID: `sui-2022-07-23-sui-cryptography-87d5950c06`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signing-type-registration-hardening`

## What Confirmed The Issue

- BcsSignable is used to enable generic BCS-based Signable and SignableBytes implementations for hashing and signing.
- The patch changes the bound from the public BcsSignable trait to bcs_signable::BcsSignable, indicating a sealed trait registration surface.
- Safety comments state implementations must be added centrally and must comply with serde_name assumptions to avoid panics.
- Local BcsSignable implementations are removed from checkpoint message types, consistent with moving eligibility into one audited location.

## What Could Have Invalidated It

- No malformed input, network path, or attacker-controlled flow is shown.
- No signature forgery, replay, type-confusion exploit, or consensus divergence is demonstrated.
- No prior unsafe implementation outside the intended set is identified.
- No concrete denial-of-service path is proven from the trace_name error handling change.

## Severity Guidance

- Expected impact band: signature-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Validate only as security hardening of a signing eligibility boundary.
- Do not claim a confirmed vulnerability or exploit fix.
- Do not retain the liveness-failure classification from the generated finding.
- Do not claim consensus, storage, or validator safety impact beyond the signing helper boundary shown in the patch.
