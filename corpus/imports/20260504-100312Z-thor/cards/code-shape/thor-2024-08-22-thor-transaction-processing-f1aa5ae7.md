# Code-Shape Card

## Metadata

- ID: `thor-2024-08-22-thor-transaction-processing-f1aa5ae7`
- Bug family: `authz_and_role_gates`
- Bug class: `debug-api-tracer-allowlist-hardening`

## Code Shape Summary

- A debug RPC path delegated caller-supplied tracer names to the tracer factory without an API-side allowlist; the fix rejects blank names and requires none/all/explicit allowlist policy before construction.

## Search Motifs

- debug endpoint accepts tracer name from request
- blank tracer name selects default tracer
- custom tracer factory reachable from RPC options
- allowCustom flag exists without per-API allowed-name gate
- CLI flag defaults sensitive plugins to none

## Typical Asymmetry

- The external or cross-context input is treated as already safe, while the later privileged sink assumes that admission, domain, or cardinality checks already happened upstream.

## Patch Pattern

- Add an operator-controlled allowlist with a deny-by-default value, trim and reject blank names, check requested tracer names before factory invocation, and return forbidden errors on denial.

## False Match Warnings

- No issue if the debug API is never exposed outside trusted operators.
- No issue if all tracer names are hardcoded server-side.
- Do not flag ordinary error-message changes without a policy gate around construction.
