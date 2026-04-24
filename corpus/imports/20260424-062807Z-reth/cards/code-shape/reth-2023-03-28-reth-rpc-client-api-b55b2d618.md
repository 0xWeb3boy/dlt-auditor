# Code-Shape Card

## Metadata

- ID: `reth-2023-03-28-reth-rpc-client-api-b55b2d618`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-penalty-misclassification`

## Code Shape Summary

- Different txpool rejection reasons were collapsed into a generic bad-import path. That conflated permanently invalid transaction composition with rejections caused by pool policy or state, leading downstream import handling to treat all failures the same.

## Search Motifs

- peer admission, listener notification, or response scheduling bypasses fork/status/policy checks
- peer-penalty-misclassification fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses remote peer response -> fetch scheduler, but peer-policy-gating is incomplete before the code updates or relies on peer selection and retry scheduling.

## Patch Pattern

- Introduce an explicit error classifier at the txpool-to-network boundary and use it to gate bad-import handling instead of treating every import failure as equivalent.

## False Match Warnings

- The patch excerpts do not show what on_bad_import and on_good_import actually do downstream
- No evidence shows concrete peer disconnects, bans, or reputation score changes caused by the old behavior
- No exploit narrative or test demonstrates that an attacker could reliably trigger security-impacting misclassification
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
