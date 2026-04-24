# Code-Shape Card

## Metadata

- ID: `optimism-2025-03-12-optimism-transaction-processing-0085136f22`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-integrity`

## Code Shape Summary

- The buggy shape was a configuration-loader or deployment pipeline that allowed data or state to approach generation or activation of privileged protocol configuration before fully enforcing configuration-validation. The initialization logic selected shared global deployment configuration based on tag/predeployed-OPCM availability alone, instead of first checking that the deployment intent was on the standard path and aligned with the canonical standard authority set.

## Search Motifs

- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified
- deployment config is applied before required security fields are checked
- chain-specific defaults overwrite or omit privileged role constraints
- unsupported mode combinations are accepted and interpreted later

## Typical Asymmetry

- The vulnerable asymmetry is that configuration-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach generation or activation of privileged protocol configuration.

## Patch Pattern

- Restrict reuse of shared privileged configuration to explicit standard-intent conditions and canonical role checks, and fail closed when canonical authority lookups cannot be resolved.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
