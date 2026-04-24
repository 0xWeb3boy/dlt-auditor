# Code-Shape Card

## Metadata

- ID: `sui-2022-12-29-sui-storage-b376f812b5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `epoch-transition-race`

## Code Shape Summary

- The patch fixes a concrete race between certificate execution and authority reconfiguration by adding an execution-epoch RwLock, requiring certificate execution to hold a read guard for the matching epoch, and requiring reconfiguration to hold a write guard while reverting uncommitted epoch transactions and advancing epoch.

## Search Motifs

- state-transition-invariant enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Add an explicit read/write concurrency guard around epoch-sensitive execution and reconfiguration, and validate certificate epoch against the guarded execution epoch before proceeding.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
