# Code-Shape Card

## Metadata

- ID: `sui-2022-12-20-sui-consensus-6c3e2bba3f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-epoch-invariant-hardening`

## Code Shape Summary

- The evidence supports a consensus/reconfiguration correctness hardening: the patch carries an intended epoch into transaction-processing paths and adds checked loading of the per-epoch store. It does not establish a vulnerability, attacker influence, exploitability, consensus fork, asset loss, or other concrete security impact.

## Search Motifs

- state-transition-invariant enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Propagate the intended epoch to consensus processing, use an epoch-checked accessor for per-epoch state, and stop or reject processing when the active store or certificate epoch does not match.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
