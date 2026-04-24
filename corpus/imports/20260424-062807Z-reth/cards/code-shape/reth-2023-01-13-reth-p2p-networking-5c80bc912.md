# Code-Shape Card

## Metadata

- ID: `reth-2023-01-13-reth-p2p-networking-5c80bc912`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-peer-validation`

## Code Shape Summary

- Discovery-sourced peer admission bypassed the existing fork-ID validation path because peers were inserted directly from the discovery handler instead of being routed through the validated swarm state-action handler.

## Search Motifs

- peer admission, listener notification, or response scheduling bypasses fork/status/policy checks
- search for `fork_id` call sites that derive, cache, or validate security-sensitive state
- insufficient-peer-validation fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses remote peer -> node networking stack, but peer-policy-gating is incomplete before the code updates or relies on peer admission, scoring, or block/transaction import.

## Patch Pattern

- Move discovery output onto a centralized state-transition path and enforce protocol-compatibility checks immediately before peer admission.

## False Match Warnings

- No evidence shows that an invalid-fork peer could successfully handshake, stay connected, or influence consensus-critical behavior
- No test, incident, or exploit evidence demonstrates real-world impact beyond admitting incompatible peers
- No evidence quantifies denial-of-service, resource exhaustion, or peer-table poisoning severity
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
