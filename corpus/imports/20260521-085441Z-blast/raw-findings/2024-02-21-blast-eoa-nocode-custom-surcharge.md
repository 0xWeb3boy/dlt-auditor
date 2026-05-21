---
case_id: m_08_eoa_nocode_custom_surcharge
project: blast
domain: blockchain-core
subsystem: execution-client-gas-accounting
bug_class: nocode-target-repeated-surcharge
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-08 Calls charge additional gas even if the target address is an EOA (#801)
impact_type:
  - "denial-of-service"
  - "fee-miscalculation"
  - "compatibility-break"
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

Calls charge additional gas even if target address is an EOA is a report-derived Blast finding from the 2024 competition. The reusable issue is: First-use storage surcharges should be tied to targets that actually create gas-accounting storage work, not no-code/EOA targets that execute no code.

## Root Cause

No-code calls return without target execution or allocation, but the repeated surcharge predicate only checks whether the target has an allocation.

## Attack Surface

- Trust boundary: EVM call graph -> Blast high-frame surcharge
- Entrypoint: CALL/STATICCALL/CALLCODE/DELEGATECALL to EOA or empty-code target
- Sensitive sink: transaction gas charge and caller-side allocation

## Preconditions And Capabilities

- Attacker capability: execute a deep call graph and repeatedly call no-code targets
- Preconditions: frame count exceeds threshold
- Preconditions: target remains with zero GasTracker allocation after the call

## Impact

Impact types: denial-of-service, fee-miscalculation, compatibility-break. Blast radius: deep call graphs and relayed transactions.

## Patch Pattern

Do not charge the storage-style surcharge for no-code targets, or record an explicit per-target surcharge marker independent of execution allocation.

## Source References

- report.md#M-08
- operations_acl.go
- evm.go no-code call path
