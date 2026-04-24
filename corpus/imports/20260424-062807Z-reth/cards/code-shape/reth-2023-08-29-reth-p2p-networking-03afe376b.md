# Code-Shape Card

## Metadata

- ID: `reth-2023-08-29-reth-p2p-networking-03afe376b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `listener-filter-bypass`

## Code Shape Summary

- A missing filter at the full transaction event fan-out point allowed the full-stream path to ignore listener-kind propagation restrictions that were already described elsewhere in the subsystem.

## Search Motifs

- Result-returning consensus/storage operation called without propagating errors
- search for `PropagateOnly` call sites that derive, cache, or validate security-sensitive state
- listener-filter-bypass fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses transaction pool policy -> network listener stream, but peer-policy-gating is incomplete before the code updates or relies on transaction propagation stream.

## Patch Pattern

- Add an explicit eligibility check at event dispatch time so restricted listeners do not receive events outside their declared scope, then align related types and API documentation to the same rule.

## False Match Warnings

- No proof that non-propagable transactions were actually broadcast to remote peers
- No proof of attacker control over the affected listener path or a practical exploit chain
- No evidence of confidentiality breach, consensus failure, or state corruption from this bug
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
