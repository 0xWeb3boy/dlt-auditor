---
case_id: m_06_high_frame_precompile_surcharge_repeat
project: blast
domain: blockchain-core
subsystem: execution-client-gas-accounting
bug_class: custom-surcharge-wrong-participant-key
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-06 BlastGasParamStorageGas should not be paid every time for precompiled contract calls (#937)
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

BlastGasParamStorageGas should not be paid every time for precompiled contract calls is a report-derived Blast finding from the 2024 competition. The reusable issue is: A storage-style first-use surcharge should be charged once for a participant that creates gas-accounting state, not repeatedly for targets that never receive allocations.

## Root Cause

The surcharge predicate checks target allocation, but precompile work is attributed to a global Blast address rather than the target, so the target always looks first-use.

## Attack Surface

- Trust boundary: EVM call graph -> Blast high-frame surcharge
- Entrypoint: CALL-family opcode after frame threshold targeting precompiles
- Sensitive sink: transaction gas charge and GasTracker allocation

## Preconditions And Capabilities

- Attacker capability: execute a deep call graph and repeatedly call a precompile target
- Preconditions: frame count exceeds BlastMaxFrameCount
- Preconditions: precompile execution does not mark the precompile address as having gas allocation

## Impact

Impact types: denial-of-service, fee-miscalculation, compatibility-break. Blast radius: contracts using deep precompile call patterns.

## Patch Pattern

Track a separate seen/surcharged target set or bind the predicate to the same participant identity that receives the allocation.

## Source References

- report.md#M-06
- operations_acl.go
- evm.go precompile paths
