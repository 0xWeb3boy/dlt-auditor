# Code-Shape Card

## Metadata

- ID: `reth-2023-01-20-reth-p2p-networking-eb11da8ad`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-handshake-state-inconsistency`

## Code Shape Summary

- Handshake metadata was assembled from separate optional builder inputs and partially independent defaults instead of being derived together from one authoritative source. That structure allowed `Status` setup and fork-filter setup to drift from the same `ChainSpec` and head context.

## Search Motifs

- peer admission, listener notification, or response scheduling bypasses fork/status/policy checks
- search for `Status` call sites that derive, cache, or validate security-sensitive state
- search for `ForkFilter` call sites that derive, cache, or validate security-sensitive state
- search for `ChainSpec` call sites that derive, cache, or validate security-sensitive state
- p2p-handshake-state-inconsistency fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses remote peer -> pending session admission, but state-coordinate-consistency is incomplete before the code updates or relies on authenticated peer session table.

## Patch Pattern

- Replace separately carried or partially defaulted handshake fields with a single derivation path that computes all related protocol metadata from shared authoritative inputs at build time.

## False Match Warnings

- No proof that the old code accepted malicious or wrong-chain peers in practice
- No test, advisory, or commit message explicitly describing a vulnerability or attack scenario
- No evidence of consensus compromise, authentication bypass, or replay exploitation from the prior behavior alone
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
