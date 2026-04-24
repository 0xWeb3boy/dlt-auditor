# Code-Shape Card

## Metadata

- ID: `optimism-2025-06-02-optimism-rpc-client-api-09dfe35bc5`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control-validation`

## Code Shape Summary

- The buggy shape was a rpc-handler or API validation path that allowed data or state to approach backend forwarding, access-list approval, or service state derived from caller input before fully enforcing authorization. The validation path did not fully encode or enforce all of the execution context and edge-case rules needed by the interop access-list check.

## Search Motifs

- role separation checked on one lifecycle path but not initialize/transfer/update
- policy gate depends on caller-supplied context that can be omitted or defaulted
- privileged address or owner field accepted without invariant checks
- rpc-handler or API validation path reaches backend forwarding, access-list approval, or service state derived from caller input with partial validation
- authorization is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that authorization was enforced only partially, late, or in one lifecycle branch while another branch could still reach backend forwarding, access-list approval, or service state derived from caller input.

## Patch Pattern

- Tighten admission checks by making required context explicit, rejecting ambiguous edge cases, and replacing manual arithmetic guards with safer helper logic.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
