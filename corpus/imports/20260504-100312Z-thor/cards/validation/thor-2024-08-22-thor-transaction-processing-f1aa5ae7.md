# Validation Card

## Metadata

- ID: `thor-2024-08-22-thor-transaction-processing-f1aa5ae7`
- Bug family: `authz_and_role_gates`
- Bug class: `debug-api-tracer-allowlist-hardening`

## What Confirmed The Issue

- api-allowed-tracers defaults to none.
- createTracer trims blank names and checks none/all/explicit allowlist before construction.
- Denied tracer creation propagates as Forbidden from the trace-call path.
- Phase 4 kept the finding as likely `security-hardening`, not as a confirmed vulnerability.

## What Could Have Invalidated It

- The endpoint is authenticated and only usable by fully trusted operators.
- The tracer factory cannot execute custom or expensive logic.
- A reverse proxy or separate policy layer already enforces an equivalent allowlist.

## Severity Guidance

- Expected impact band: low to medium node-local hardening
- Expected severity band: `medium_or_low`
- Rationale: The change is deny-by-default hardening for a sensitive debug API. It reduces local node/API abuse risk, but the evidence does not prove external exposure or a concrete exploit.

## False-Positive Cautions

- No issue if the debug API is never exposed outside trusted operators.
- No issue if all tracer names are hardcoded server-side.
- Do not flag ordinary error-message changes without a policy gate around construction.
