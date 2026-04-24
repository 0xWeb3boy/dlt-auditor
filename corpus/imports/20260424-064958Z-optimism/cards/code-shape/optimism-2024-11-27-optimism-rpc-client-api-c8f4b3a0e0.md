# Code-Shape Card

## Metadata

- ID: `optimism-2024-11-27-optimism-rpc-client-api-c8f4b3a0e0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `security-sensitive-config-validation`

## Code Shape Summary

- The buggy shape was a rpc-handler or API validation path that allowed data or state to approach backend forwarding, access-list approval, or service state derived from caller input before fully enforcing configuration-validation. Validation and normalization of standard deployment intents were not clearly enforced at the apply entrypoint, leaving standard-chain values and role fields to be handled in a more fragmented way.

## Search Motifs

- role separation checked on one lifecycle path but not initialize/transfer/update
- policy gate depends on caller-supplied context that can be omitted or defaulted
- privileged address or owner field accepted without invariant checks
- deployment config is applied before required security fields are checked
- chain-specific defaults overwrite or omit privileged role constraints
- unsupported mode combinations are accepted and interpreted later

## Typical Asymmetry

- The vulnerable asymmetry is that configuration-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach backend forwarding, access-list approval, or service state derived from caller input.

## Patch Pattern

- Centralize pre-execution validation and standard-value normalization for deployment intents, using canonical chain-specific data where needed.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
