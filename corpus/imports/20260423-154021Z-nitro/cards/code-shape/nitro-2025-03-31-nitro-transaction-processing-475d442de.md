# Code-Shape Card

## Metadata

- ID: `nitro-2025-03-31-nitro-transaction-processing-475d442de`
- Bug family: `authz_and_role_gates`
- Bug class: `stale-authorization-state`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch is clearly hardening the express-lane admission path against stale or improperly validated submissions, but the provided evidence does not firmly establish a concrete vulnerability beyond correctness and fail-closed behavior.

## Search Motifs

- Motif 1: authorization decisions read from local round-control caches instead of the authoritative tracker
- Motif 2: tracker-backed validation is added at ingress after earlier code performed only nil or shape checks
- Motif 3: comments mention stale messages around round transfer, handoff, or epoch end

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed formatting or shallow admission checks at ingress, but the authoritative policy, payment, version, or sequencing invariant was enforced only later or from weaker context.

## Patch Pattern

- What the fix changed structurally: Replace local/cached authorization lookups with tracker-backed validation at admission time and fail closed when the authoritative validator is unavailable.

## False Match Warnings

- What looks similar but is often not a bug: If a later authoritative validator rejects the same input before it can affect persistent state, similar cases may reduce to wasted work rather than a security bug.
