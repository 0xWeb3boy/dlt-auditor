# Code-Shape Card

## Metadata

- ID: `reth-2025-09-25-reth-rpc-client-api-aa192c255`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-auth-header-parsing`

## Code Shape Summary

- The parser used substring search instead of an anchored prefix check for the Bearer scheme. That made the helper overly permissive about Authorization header format and allowed malformed values to be normalized into a candidate token for later JWT validation.

## Search Motifs

- improper-auth-header-parsing fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses http client -> authenticated rpc middleware, but authentication-header-canonicalization is incomplete before the code updates or relies on jwt-protected rpc method access.

## Patch Pattern

- Replace permissive substring-based authentication-scheme parsing with exact prefix validation, then add a regression test for malformed header values that previously matched accidentally.

## False Match Warnings

- No proof that a malformed header could bypass authentication without a valid JWT
- No evidence of downstream parser disagreement or request smuggling impact
- No exploit, advisory, or end-to-end unauthorized access scenario is shown in the patch
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
