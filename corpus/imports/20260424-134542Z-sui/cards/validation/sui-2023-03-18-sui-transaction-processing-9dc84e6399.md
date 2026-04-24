# Validation Card

## Metadata

- ID: `sui-2023-03-18-sui-transaction-processing-9dc84e6399`
- Bug family: `authz_and_role_gates`
- Bug class: `object-access-authentication-invariant`

## What Confirmed The Issue

- Commit message explicitly identifies authenticated object reads as a key security property of Sui transactions.
- Execution path now calls check_ownership_invariants before effects are produced.
- TemporaryStore gains logic to determine objects requiring authentication versus already authenticated objects.
- The check is skipped only for arbitrary-function-call/dev-inspect mode in the shown code.

## What Could Have Invalidated It

- No concrete exploit path or externally triggerable unauthenticated read is shown.
- The added check is #[cfg(debug_assertions)], so production enforcement is not established.
- Provided test evidence is not detailed enough to prove a vulnerability regression.
- No evidence supports the original liveness-failure classification.

## Severity Guidance

- Expected impact band: unauthorized-object-read
- Expected severity band: high
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Validate as security hardening for transaction object-access invariant checking.
- Do not claim a confirmed production vulnerability or consensus break from this evidence alone.
- Do not classify as liveness impact based on the supplied patch.
- Do not treat the debug-only unwrap as a production error-handling security fix.
