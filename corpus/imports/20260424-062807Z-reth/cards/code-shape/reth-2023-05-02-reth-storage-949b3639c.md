# Code-Shape Card

## Metadata

- ID: `reth-2023-05-02-reth-storage-949b3639c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invalid-ancestor-handling`

## Code Shape Summary

- The pre-fix forkchoice failure path treated canonicalization errors too generically. Based on the added invalid-header cache and ancestor check, the missing behavior was retention and reuse of invalid ancestry information when later forkchoice updates referenced the same invalid head or its descendants.

## Search Motifs

- block accepted or scheduled before parent-relative header/ancestor consistency checks
- invalid-ancestor-handling fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses forkchoice or sidechain state -> persistent storage provider, but parent-and-ancestor-validation is incomplete before the code updates or relies on canonical state view, fork ancestry, or persisted trie updates.

## Patch Pattern

- Separate known-invalid state from generic error recovery by caching invalid items and consulting that cache at the failure boundary.

## False Match Warnings

- No proof that the pre-patch behavior let an attacker make the node accept an invalid block as canonical
- No evidence of a demonstrated consensus split, slashing event, fund impact, or remote exploit path
- No test or commit text is provided showing the exact failure mode observed in production
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
