# Code-Shape Card

## Metadata

- ID: `bor-2026-01-27-bor-rpc-client-api-df8f2a879`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-peer-data-verification`

## Code Shape Summary

- The provided diff supports that witness fetching was refactored into a verification-aware path and that metadata page-count querying was added, but it does not establish a concrete vulnerability or exploit from the shown code alone. This is security-relevant hardening at most from the available evidence, so the security conclusion should be downgraded to unclear. Root cause: The visible issue is that the shown witness-fetch call sites did not consistently use the verification-aware request path. The patch centralizes those requests and adds a metadata-query helper with basic guards. The provided evidence does not prove a stronger root cause such as a consensus break, full witness forgery acceptance, or a demonstrated denial-of-service vulnerability.

## Search Motifs

- RPC method continues after backend error or returns success with partial/unchecked data
- public query accepts unbounded range, path, or selector before authorization and limit checks
- administrative or debug endpoint exposes privileged behavior without explicit gating

## Typical Asymmetry

- Attacker-controlled data crosses external RPC client to node service boundary and reaches backend state access, privileged API behavior, or response serialization before the missing property is enforced.

## Patch Pattern

- Centralize a network request behind a single verification-aware helper, and add a lightweight metadata query plus enforcement hooks so callers do not bypass the checked path.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- RPC findings are lower risk when the method is disabled by default, authenticated, strictly local-only, or returns only non-sensitive metadata.
