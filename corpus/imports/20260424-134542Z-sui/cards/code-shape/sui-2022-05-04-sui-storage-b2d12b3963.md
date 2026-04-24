# Code-Shape Card

## Metadata

- ID: `sui-2022-05-04-sui-storage-b2d12b3963`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-metering-inconsistency`

## Code Shape Summary

- The supported finding is a likely gas-metering consistency fix. The clearest evidence is that `transaction_input_checker.rs::check_locks` now sums the gas-metered sizes of all checked input objects and calls `gas_status.charge_storage_read(total_size)?` before returning them.

## Search Motifs

- resource-accounting enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The storage sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Add explicit gas charging at the transaction-input boundary and align gateway object preparation with authority-backed object availability.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
