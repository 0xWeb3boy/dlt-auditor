# Validation Card

## Metadata

- ID: `sui-2022-02-06-sui-staking-db9ee35c05`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `byzantine-authority-robustness`

## What Confirmed The Issue

- New authority aggregation helper is documented as allowing per-authority errors to be consumed so Byzantine authorities cannot interrupt the logic.
- Object-info query path no longer unwraps parent_certificate with expect; it only proceeds when a checked certificate is present.
- ObjectInfoResponse and parent_sync semantics are expanded to expose latest object references and deleted-object certificate history for synchronization.

## What Could Have Invalidated It

- No exploit scenario, attack test, advisory, or demonstrated asset/state compromise is provided.
- No evidence shows a consensus safety break, double-spend, authorization bypass, or concrete state-corruption vulnerability.
- The patch includes broad robustness and API semantics work, so not all changes are security-specific.

## Severity Guidance

- Expected impact band: availability_or_sync-integrity
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Classify as security-hardening for adversarial authority tolerance, not as a proven security-fix.
- Do not retain the original staking label; changed files point to FastPay authority/client synchronization.
- Do not claim state corruption or state-integrity impact beyond conservative sync-integrity hardening.
