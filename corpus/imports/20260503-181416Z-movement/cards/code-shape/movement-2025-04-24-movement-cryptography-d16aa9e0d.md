# Code-Shape Card

## Metadata

- ID: `movement-2025-04-24-movement-cryptography-d16aa9e0d`
- Bug family: `authz_and_role_gates`
- Bug class: `transaction-validation-bypass`

## Code Shape Summary

- Baseline Aptos transaction prevalidation was coupled to optional whitelist configuration. With no whitelist, the sequencer installed no prevalidator and batch_write could skip validation. The fix always constructs a validator and makes whitelist enforcement an optional mode inside it.

## Search Motifs

- prevalidator: Option<Validator> set to None when whitelist config is absent
- batch_write matches on optional prevalidator before accepting transactions
- patch creates Validator::new for no-whitelist mode
- whitelist policy moved inside validator rather than around validator existence

## Typical Asymmetry

- An optional whitelist policy accidentally controlled whether the mandatory baseline validator existed at all.

## Patch Pattern

- Always instantiate and invoke the baseline transaction validator, use with_whitelist only to add optional sender policy, and accept only Prevalidated transactions while discarding validation errors.

## False Match Warnings

- Do not flag if no-whitelist mode is unreachable or explicitly trusted/admin-only.
- Do not claim whitelist enforcement was broken when a whitelist was configured.
- Do not claim signature forgery without showing what prevalidate checks and what downstream accepts.
