# Code-Shape Card

## Metadata

- ID: `optimism-2025-03-12-optimism-transaction-processing-060a261c6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-scoping`

## Code Shape Summary

- The buggy shape was a configuration-loader or deployment pipeline that allowed data or state to approach generation or activation of privileged protocol configuration before fully enforcing configuration-validation. The init logic chose a shared global configuration path from deployment-environment properties (isL1Tag and predeployed OPCM availability) without first constraining that choice to intents that actually matched the standard deployment model and standard role assumptions.

## Search Motifs

- deployment config is applied before required security fields are checked
- chain-specific defaults overwrite or omit privileged role constraints
- unsupported mode combinations are accepted and interpreted later
- configuration-loader or deployment pipeline reaches generation or activation of privileged protocol configuration with partial validation
- configuration-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that configuration-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach generation or activation of privileged protocol configuration.

## Patch Pattern

- Restrict a broad default/shared configuration path to explicitly eligible intent types, and back that decision with fail-closed validation of canonical role and owner data.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
