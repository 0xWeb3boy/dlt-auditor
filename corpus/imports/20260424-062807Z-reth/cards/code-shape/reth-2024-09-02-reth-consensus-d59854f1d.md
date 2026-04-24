# Code-Shape Card

## Metadata

- ID: `reth-2024-09-02-reth-consensus-d59854f1d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-runtime-bound-check`

## Code Shape Summary

- The shown root cause is reliance on a debug-only precondition for an input relationship that the function actually needed at runtime. The helper trusted callers to keep `finalized_num` within `upper_bound` instead of enforcing that bound inside the removal logic.

## Search Motifs

- search for `remove_until` call sites that derive, cache, or validate security-sensitive state
- search for `min(upper_bound)` call sites that derive, cache, or validate security-sensitive state
- search for `finalized_num` call sites that derive, cache, or validate security-sensitive state
- missing-runtime-bound-check fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses consensus layer signal -> execution client forkchoice/block state, but numeric-bound-validation is incomplete before the code updates or relies on canonical head, payload status, or pipeline scheduling.

## Patch Pattern

- Replace a debug-only invariant check with runtime input normalization at the state-transition boundary, and document the resulting edge-case behavior explicitly.

## False Match Warnings

- No evidence shows that untrusted peers or external inputs can force finalized_num > upper_bound
- No reproducer or test demonstrates harmful pre-patch behavior in release builds
- No proof is provided of consensus divergence, chain split, persistence corruption, or validator compromise
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
