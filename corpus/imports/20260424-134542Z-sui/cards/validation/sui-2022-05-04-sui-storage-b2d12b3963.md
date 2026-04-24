# Validation Card

## Metadata

- ID: `sui-2022-05-04-sui-storage-b2d12b3963`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-metering-inconsistency`

## What Confirmed The Issue

- `check_locks` now sums `object_size_for_gas_metering()` across input objects.
- The patch calls `gas_status.charge_storage_read(total_size)?` before returning checked objects.
- Commit subject explicitly frames the change as making gateway gas metering consistent with authority behavior.
- Gateway code adds synchronization of missing input objects from authorities before execution.

## What Could Have Invalidated It

- No test assertion is shown proving an exploitable undercharging scenario.
- No evidence shows transactions could execute for free or bypass gas budget enforcement entirely.
- No evidence supports state corruption, ownership bypass, signature validation failure, or consensus compromise.
- No before/after runtime behavior or advisory confirms security impact beyond metering consistency.

## Severity Guidance

- Expected impact band: resource-accounting_or_economic-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Treat as gas/resource accounting hardening, not a proven exploit fix.
- Do not claim state integrity corruption from the supplied patch alone.
- Do not claim consensus or signature security impact.
- Do not claim arbitrary transaction execution or full gas bypass.
