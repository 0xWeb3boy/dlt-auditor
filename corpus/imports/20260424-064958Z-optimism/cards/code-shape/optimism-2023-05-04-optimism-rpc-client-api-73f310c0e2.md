# Code-Shape Card

## Metadata

- ID: `optimism-2023-05-04-optimism-rpc-client-api-73f310c0e2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-consensus-validation`

## Code Shape Summary

- The buggy shape was a rpc-handler or API validation path that allowed data or state to approach backend forwarding, access-list approval, or service state derived from caller input before fully enforcing protocol-state-invariant. The consensus-aware forwarding path enforced backend selection but, based on the provided evidence, did not also enforce block-tag or block-number compliance with the tracked consensus height before forwarding requests.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- rpc-handler or API validation path reaches backend forwarding, access-list approval, or service state derived from caller input with partial validation
- protocol-state-invariant is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that protocol-state-invariant was enforced only partially, late, or in one lifecycle branch while another branch could still reach backend forwarding, access-list approval, or service state derived from caller input.

## Patch Pattern

- Add a pre-dispatch validation and normalization gate that derives authoritative consensus state, rewrites or rejects incompatible requests, and short-circuits invalid inputs before backend execution.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
