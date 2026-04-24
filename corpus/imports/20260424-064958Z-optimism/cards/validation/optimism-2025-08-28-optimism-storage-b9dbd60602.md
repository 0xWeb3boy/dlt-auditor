# Validation Card

## Metadata

- ID: `optimism-2025-08-28-optimism-storage-b9dbd60602`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation`

## What Confirmed The Issue

- Resetter::reset now resolves derived_to_source(local_safe.id()) before proceeding.
- The new is_canonical(chain_id, source.id()) check rejects non-canonical L1 provenance.
- The code fails closed with ManagedNodeError::ResetFailed instead of continuing reset on stale state.
- The changed path is runtime recovery/reset logic for a managed sync node, which is integrity-sensitive in a blockchain system.

## What Could Have Invalidated It

- No evidence that an external attacker can trigger the race or steer reset behavior.
- No proof of concrete exploit outcomes such as consensus split, fund loss, or privilege gain.
- No advisory, CVE, or commit text explicitly frames this as a security vulnerability.
- The patch alone does not show that pre-fix behavior caused actual state corruption beyond incorrect recovery handling.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No evidence that an external attacker can trigger the race or steer reset behavior.
- No proof of concrete exploit outcomes such as consensus split, fund loss, or privilege gain.
- No advisory, CVE, or commit text explicitly frames this as a security vulnerability.
