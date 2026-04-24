# Code-Shape Card

## Metadata

- ID: `optimism-2025-02-18-optimism-rpc-client-api-6e39803ab8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verification-config-inconsistency`

## Code Shape Summary

- The buggy shape was a rpc-handler or API validation path that allowed data or state to approach backend forwarding, access-list approval, or service state derived from caller input before fully enforcing configuration-validation. The grounded root cause is inconsistent sourcing of dependency-set state: one path rebuilt the dependency set inside consolidation while the patched code treats it as boot-provided configuration that should be loaded and threaded through directly.

## Search Motifs

- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified
- deployment config is applied before required security fields are checked
- chain-specific defaults overwrite or omit privileged role constraints
- unsupported mode combinations are accepted and interpreted later

## Typical Asymmetry

- The vulnerable asymmetry is that configuration-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach backend forwarding, access-list approval, or service state derived from caller input.

## Patch Pattern

- Stop reconstructing shared configuration inside a downstream checker and instead load the canonical object from the upstream boot/config source and pass it through explicitly.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
