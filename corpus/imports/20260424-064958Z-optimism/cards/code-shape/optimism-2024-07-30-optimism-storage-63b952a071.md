# Code-Shape Card

## Metadata

- ID: `optimism-2024-07-30-optimism-storage-63b952a071`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-validation`

## Code Shape Summary

- The buggy shape was a configuration-loader or deployment pipeline that allowed data or state to approach generation or activation of privileged protocol configuration before fully enforcing configuration-validation. Insufficient validation of deploy-config inputs allowed more invalid or incomplete deployment settings to pass configuration checks than the patched code now permits.

## Search Motifs

- deployment config is applied before required security fields are checked
- chain-specific defaults overwrite or omit privileged role constraints
- unsupported mode combinations are accepted and interpreted later
- configuration-loader or deployment pipeline reaches generation or activation of privileged protocol configuration with partial validation
- configuration-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that configuration-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach generation or activation of privileged protocol configuration.

## Patch Pattern

- Add explicit fail-closed validation for required deploy-config fields and supported parameter combinations in config checker methods.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
