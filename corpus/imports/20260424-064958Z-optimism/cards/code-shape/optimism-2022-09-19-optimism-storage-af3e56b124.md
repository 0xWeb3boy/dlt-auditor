# Code-Shape Card

## Metadata

- ID: `optimism-2022-09-19-optimism-storage-af3e56b124`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control-invariant-bypass`

## Code Shape Summary

- The buggy shape was a state-storage or reset/reorg handling path that allowed data or state to approach stored canonicality, proof-window, or derived-state update before fully enforcing authorization. The distinct-role invariant appears to have been enforced on one mutation path (changeProposer) but not on other paths that could assign the same privileged roles, especially initialization and default ownership transfer behavior.

## Search Motifs

- role separation checked on one lifecycle path but not initialize/transfer/update
- policy gate depends on caller-supplied context that can be omitted or defaulted
- privileged address or owner field accepted without invariant checks
- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified

## Typical Asymmetry

- The vulnerable asymmetry is that authorization was enforced only partially, late, or in one lifecycle branch while another branch could still reach stored canonicality, proof-window, or derived-state update.

## Patch Pattern

- Apply the same access-control invariant on every state-entry path that can assign privileged roles, including initialization and inherited admin helpers.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
