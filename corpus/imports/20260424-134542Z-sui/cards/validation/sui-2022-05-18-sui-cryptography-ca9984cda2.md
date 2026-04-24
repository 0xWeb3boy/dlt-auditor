# Validation Card

## Metadata

- ID: `sui-2022-05-18-sui-cryptography-ca9984cda2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-input-validation`

## What Confirmed The Issue

- Adds fp_ensure!(certificate.contains_shared_object(), SuiError::NotASharedObjectTransaction) before shared-object consensus handling continues.
- Patch comment explicitly frames the boundary as exposed to arbitrary input from Byzantine authorities.
- try_skip_consensus also enforces the shared-object certificate invariant before shortcut execution behavior.
- shared_locks_exist change appears to tighten lock attribution before immediate execution.

## What Could Have Invalidated It

- No exploit scenario or advisory is provided.
- No evidence shows non-shared-object certificates could cause state corruption or unauthorized finalization.
- No cryptographic verification or signature-validation flaw is demonstrated.
- Narwhal configuration changes are test-speed support, not production security evidence.

## Severity Guidance

- Expected impact band: consensus-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as consensus input-validation hardening, not a confirmed vulnerability fix.
- Do not retain the original cryptography or signature framing.
- Do not claim proven state corruption or arbitrary transaction finalization.
- Impact should be limited to protecting consensus/shared-object execution invariants.
