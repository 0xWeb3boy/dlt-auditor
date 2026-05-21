---
case_id: m_01_invalid_yield_precompile_zero_gas
project: blast
domain: blockchain-core
subsystem: execution-client-native-precompile
bug_class: invalid-precompile-revert-undercharge
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-01 Blast precompile reverts cost zero gas, allowing resource consumption related DOS (#1105)
impact_type:
  - "denial-of-service"
  - "resource-accounting"
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

Blast precompile reverts cost zero gas allowing resource consumption related DoS is a report-derived Blast finding from the 2024 competition. The reusable issue is: Malformed or unknown native precompile calls should still charge enough gas for native dispatch, parsing, rollback, and attribution work.

## Root Cause

Invalid precompile calls reach native selector parsing and revert handling while RequiredGas is zero and remaining gas is returned to the caller.

## Attack Surface

- Trust boundary: EVM call -> native precompile error handling
- Entrypoint: CALL/STATICCALL to Blast yield precompile with invalid calldata
- Sensitive sink: RunPrecompiledContract revert path and GasTracker attribution

## Preconditions And Capabilities

- Attacker capability: submit transactions or contract loops that call the native precompile with malformed calldata
- Preconditions: invalid selector returns zero RequiredGas
- Preconditions: revert returns unused subcall gas without charging native body work

## Impact

Impact types: denial-of-service, resource-accounting. Blast radius: execution-client block processing.

## Patch Pattern

Charge a minimum invalid-call cost or make malformed dispatch consume the intended native precompile gas before returning a revert.

## Source References

- report.md#M-01
- blast-geth/core/vm/contracts.go
