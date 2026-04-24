# Code-Shape Card

## Metadata

- ID: `optimism-2026-04-14-optimism-transaction-processing-f491292ace`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validation-configuration-mismatch`

## Code Shape Summary

- The buggy shape was a configuration-loader or deployment pipeline that allowed data or state to approach generation or activation of privileged protocol configuration before fully enforcing configuration-validation. The shown root cause is inconsistent propagation of the configured message expiry window: the supernode interop path used a default or hardcoded value instead of the dependency-set override, and runtime wiring did not always carry the overridden dependency set forward.

## Search Motifs

- deployment config is applied before required security fields are checked
- chain-specific defaults overwrite or omit privileged role constraints
- unsupported mode combinations are accepted and interpreted later
- configuration-loader or deployment pipeline reaches generation or activation of privileged protocol configuration with partial validation
- configuration-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that configuration-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach generation or activation of privileged protocol configuration.

## Patch Pattern

- Replace a hardcoded default with dependency-set-sourced configuration, and propagate override-bearing config objects through runtime construction. Add regression support code to exercise the affected path.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
