# Code-Shape Card

## Metadata

- ID: `sui-2023-03-06-sui-consensus-e4c9e8c80c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unverified-consensus-timestamp-source`

## Code Shape Summary

- The patch likely fixes a security-relevant consensus timestamp-source bug. The consensus handler previously passed `consensus_output.sub_dag.leader.metadata.created_at` into the consensus commit prologue. The commit message states that certificate metadata timestamps are not verified and could lead to security issues.

## Search Motifs

- state-transition-invariant enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Replace use of an unverified metadata timestamp with a timestamp field documented as having consensus-enforced invariants, and pass the selected primitive value explicitly through downstream commit-boundary APIs.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
