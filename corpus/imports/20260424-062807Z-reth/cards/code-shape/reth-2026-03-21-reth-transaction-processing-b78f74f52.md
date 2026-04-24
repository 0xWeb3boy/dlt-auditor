# Code-Shape Card

## Metadata

- ID: `reth-2026-03-21-reth-transaction-processing-b78f74f52`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass`

## Code Shape Summary

- Special handling for synthetic or segmented `env_switches` blocks was implemented as broad validator exceptions in core validation code, including zero-hash sentinel logic and an `env_switches` guard around state-root checking, instead of limiting the exception to the specific receipt-derived fields described in the patch.

## Search Motifs

- authenticated trie/proof path drops empty-root, revealed-node, or rollback state needed for valid output
- search for `env_switches` call sites that derive, cache, or validate security-sensitive state
- validation-bypass fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses block or transaction input -> execution-layer validator, but validation-gate-enforcement is incomplete before the code updates or relies on transaction acceptance or consensus rule application.

## Patch Pattern

- Replace broad special-case validator bypasses with a dedicated narrow-path validator that preserves core integrity checks and skips only the fields explicitly known to be non-comparable for that block form.

## False Match Warnings

- No proof that untrusted production inputs could trigger the old bypasses
- No evidence of a demonstrated exploit, consensus split, or accepted malformed block before the patch
- No direct patch evidence showing the exact runtime exposure of benchmark or replay-related paths
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
