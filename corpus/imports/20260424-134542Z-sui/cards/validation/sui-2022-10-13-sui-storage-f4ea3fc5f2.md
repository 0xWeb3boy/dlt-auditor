# Validation Card

## Metadata

- ID: `sui-2022-10-13-sui-storage-f4ea3fc5f2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `epoch-state-confusion`

## What Confirmed The Issue

- Validator/node-sync code changes certificate retrieval from digest-only storage lookup to get_cert(epoch_id, digest).
- The new path asserts that the returned certificate epoch matches the requested epoch.
- Commit message explicitly describes a stale epoch-N certificate later causing an attempt to execute a certificate from the wrong epoch.
- Consensus transaction handling now schedules certificates through add_pending_certificates instead of only persisting certificate data.

## What Could Have Invalidated It

- No proof that an external attacker can reliably create or exploit the timing window.
- No demonstrated asset theft, unauthorized state transition, or signature forgery.
- No evidence of a full consensus safety or liveness failure across validators.
- DB dump changes are maintenance/tooling support and not independently security-relevant.

## Severity Guidance

- Expected impact band: consensus-integrity_or_state-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as security-hardening rather than security-fix.
- Do not claim confirmed exploitability from the supplied patch alone.
- Do not claim financial loss, authentication bypass, or cryptographic failure.
- The supported claim is limited to tightening epoch-scoped certificate/state handling in validator consensus-adjacent code.
