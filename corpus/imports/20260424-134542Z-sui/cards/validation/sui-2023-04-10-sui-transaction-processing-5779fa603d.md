# Validation Card

## Metadata

- ID: `sui-2023-04-10-sui-transaction-processing-5779fa603d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `monetary-accounting-invariant-hardening`

## What Confirmed The Issue

- Commit subject explicitly frames the change as hardening for an expensive per-transaction conservation check.
- New config field documents checking total SUI in transaction inputs against outputs plus gas fees.
- Authority execution path now passes the configured deep conservation-check flag into transaction execution.
- Accessor enables the check when configured or in debug builds.

## What Could Have Invalidated It

- No concrete pre-patch vulnerability or exploit path is shown.
- No evidence that production nodes enable the check by default.
- No actual failing transaction, accounting bypass, or supply-inflation scenario is demonstrated.
- Execution-engine evidence mostly shows surrounding conservation-check comments, not the full conditional enforcement logic.

## Severity Guidance

- Expected impact band: asset-integrity
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Classify as security hardening around monetary accounting invariants, not as a confirmed vulnerability fix.
- Do not claim denial of service, liveness failure, malformed transaction parsing, signature validation, or consensus failure from this evidence.
- Do not claim production impact unless separate evidence shows the option was enabled in production configurations.
- The supported impact is conservative asset/accounting integrity risk detection, not proven asset loss.
