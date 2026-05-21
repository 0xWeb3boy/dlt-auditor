---
case_id: m_18_native_yield_gas_refund_undermetering
project: blast
domain: blockchain-core
subsystem: execution-client-native-accounting
bug_class: native-bookkeeping-undermetering
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-18 Risk of DOS caused by under compensating gas for native yield and native gas refund features (#156)
impact_type:
  - "denial-of-service"
  - "resource-accounting"
  - "fee-bypass"
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

Risk of DoS caused by under compensating gas for native yield and native gas refund features is a report-derived Blast finding from the 2024 competition. The reusable issue is: Gas costs for opcodes and transactions should cover the extra native bookkeeping added by yield and gas-refund features, including per-account and global predeploy storage effects.

## Root Cause

Native yield mutates share/fixed/remainder fields and global share counts during ordinary balance operations, while gas-refund finalization iterates allocations and writes gas-parameter storage after EVM execution.

## Attack Surface

- Trust boundary: EVM transaction/opcode gas schedule -> Blast native StateDB side effects
- Entrypoint: balance changes, selfdestruct, gas allocation finalization, claimable gas updates
- Sensitive sink: Shares and Gas predeploy storage plus StateDB journals

## Preconditions And Capabilities

- Attacker capability: fill blocks with value transfers, selfdestructs, claimable contracts, or gas-heavy calls that trigger native bookkeeping
- Preconditions: native bookkeeping runs outside normal EVM opcode charging
- Preconditions: custom surcharge only covers part of the added work

## Impact

Impact types: denial-of-service, resource-accounting, fee-bypass. Blast radius: execution-client block processing.

## Patch Pattern

Benchmark and explicitly charge native-yield balance/share-count work and gas-refund finalizer work, including intrinsic or opcode-level surcharges that are not refunded back to attackers.

## Source References

- report.md#M-18
- state_object.go
- statedb.go
- gas_tracker.go
- Gas.sol
