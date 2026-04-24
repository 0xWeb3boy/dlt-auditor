# Code-Shape Card

## Metadata

- ID: `reth-2024-04-25-reth-rpc-client-api-33e7e0208`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-bad-peer-penalization`

## Code Shape Summary

- The block-bodies response path was not using the same response-quality tracking and follow-up gating already visible in the adjacent headers-response path, so peer deranking was incomplete in this part of the scheduler.

## Search Motifs

- peer admission, listener notification, or response scheduling bypasses fork/status/policy checks
- search for `next_best_peer()` call sites that derive, cache, or validate security-sensitive state
- search for `last_response_likely_bad` call sites that derive, cache, or validate security-sensitive state
- insufficient-bad-peer-penalization fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses remote peer response -> fetch scheduler, but peer-policy-gating is incomplete before the code updates or relies on peer selection and retry scheduling.

## Patch Pattern

- Propagate response-quality signals into peer state and use the best-eligible-peer selector when dispatching new work.

## False Match Warnings

- No proof that the pre-patch behavior enabled a concrete exploit or attacker-triggered denial of service
- No quantitative evidence of resource exhaustion, queue growth, or network-wide availability impact
- No evidence that empty bodies responses are always malicious rather than benign protocol edge cases
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
