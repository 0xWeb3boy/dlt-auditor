---
case_id: m_15_reverted_tx_gas_allocation_profit
project: blast
domain: blockchain-core
subsystem: gas-fee-attribution
bug_class: non-rollbacked-sidecar-accounting
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-15 Exploiting Gas Allocation Mechanics On Reverted Transactions To Profit From Spamming The Network (#626)
impact_type:
  - "fee-bypass"
  - "unauthorized-value-shift"
  - "state-machine-inconsistency"
confidence: high
tags:
  - "rollup"
  - "bridge"
  - "evm"
  - "native-yield"
validation_status: completed
security_verdict: confirmed
validated_as: competition-finding
keep_in_security_corpus: true
---

# Summary

Exploiting gas allocation mechanics on reverted transactions is a report-derived Blast finding from the 2024 competition. The reusable issue is: Per-frame gas attribution sidecars should follow EVM rollback semantics when the attributed contract state and call frame revert.

## Root Cause

StateDB snapshots roll back storage/logs/refunds, but the transaction-local GasTracker allocation map is not journaled and is finalized anyway.

## Attack Surface

- Trust boundary: EVM execution/revert -> post-transaction gas finalizer
- Entrypoint: reverting claimable-gas contract frame or failed transaction
- Sensitive sink: GasTracker.AllocateDevGas persistent claimable balance

## Preconditions And Capabilities

- Attacker capability: execute or induce paid work inside an attacker-governed claimable contract that reverts
- Preconditions: GasTracker allocation is not snapshotted with StateDB
- Preconditions: AllocateDevGas runs after the revert

## Impact

Impact types: fee-bypass, unauthorized-value-shift, state-machine-inconsistency. Blast radius: victim or sponsor paid transaction gas.

## Patch Pattern

Snapshot or roll back gas attribution entries for reverted frames, or define/restrict claimability for failed work explicitly.

## Source References

- report.md#M-15
- state_transition.go
- evm.go
- gas_tracker.go
