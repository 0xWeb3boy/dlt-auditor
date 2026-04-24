# Code-Shape Card

## Metadata

- ID: `optimism-2022-06-17-optimism-storage-35757456bf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `oracle-output-key-mismatch`

## Code Shape Summary

- The buggy shape was a state-storage or reset/reorg handling path that allowed data or state to approach stored canonicality, proof-window, or derived-state update before fully enforcing integrity-binding. The visible issue is inconsistent identity selection across the oracle/proposer path: some logic was anchored to timestamps and timestamp-derived block lookup instead of directly using the L2 block number.

## Search Motifs

- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified
- state-storage or reset/reorg handling path reaches stored canonicality, proof-window, or derived-state update with partial validation
- integrity-binding is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that integrity-binding was enforced only partially, late, or in one lifecycle branch while another branch could still reach stored canonicality, proof-window, or derived-state update.

## Patch Pattern

- Replace derived or secondary identifiers with a single canonical identifier across producer and consumer paths.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
