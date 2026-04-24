# Code-Shape Card

## Metadata

- ID: `reth-2024-03-19-reth-p2p-networking-1ad50d148`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-handshake-timeout`

## Code Shape Summary

- The direct code-level issue shown is that pending session authentication was not explicitly bounded by a timeout in the changed path. A secondary cleanup in the same patch normalizes handshake errors into the pending-session error type. The evidence does not establish more than that.

## Search Motifs

- peer admission, listener notification, or response scheduling bypasses fork/status/policy checks
- search for `PendingSessionHandshakeError::Eth` call sites that derive, cache, or validate security-sensitive state
- missing-handshake-timeout fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses remote peer -> pending session admission, but session-timeout-enforcement is incomplete before the code updates or relies on authenticated peer session table.

## Patch Pattern

- Add an explicit timeout around pending asynchronous session setup, and normalize failure reporting into the subsystem's canonical error type.

## False Match Warnings

- The patch excerpt does not show all call sites using the new timeout helper
- The evidence does not quantify whether pending sessions could actually exhaust slots or other resources in practice
- No test, advisory, or bug report is provided to prove attacker-driven denial of service
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
