---
case_id: h_05_yield_precompile_zero_required_gas
project: blast
domain: blockchain-core
subsystem: execution-client-native-precompile
bug_class: native-precompile-requiredgas-predicate
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: H-05 DoS due to Yield Precompile Always Charging 0 Gas (#787)
impact_type:
  - "denial-of-service"
  - "fee-bypass"
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

DoS due to Yield Precompile Always Charging 0 Gas is a report-derived Blast finding from the 2024 competition. The reusable issue is: Every valid native precompile selector should charge its intended RequiredGas before executing native state reads, writes, and share accounting.

## Root Cause

The selector table is placed under the wrong branch of selector parsing, so valid ABI calldata skips the intended per-selector gas costs and returns zero RequiredGas.

## Attack Surface

- Trust boundary: EVM call -> native precompile execution
- Entrypoint: CALL/STATICCALL to Blast yield precompile
- Sensitive sink: StateDB yield accounting and Shares predeploy storage

## Preconditions And Capabilities

- Attacker capability: call read selectors directly
- Attacker capability: use authorized wrapper paths for configure or claim selectors
- Preconditions: RequiredGas dispatch falls through for valid selectors
- Preconditions: native work is reachable after the zero-cost check

## Impact

Impact types: denial-of-service, fee-bypass, resource-accounting. Blast radius: execution-client block processing.

## Patch Pattern

Fix selector dispatch so valid selectors return their intended nonzero costs, and add tests for valid and invalid selector metering.

## Source References

- report.md#H-05
- blast-geth/core/vm/contracts.go
