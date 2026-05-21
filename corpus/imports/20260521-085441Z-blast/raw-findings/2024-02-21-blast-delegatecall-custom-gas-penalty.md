---
case_id: m_19_delegatecall_custom_gas_penalty
project: blast
domain: blockchain-core
subsystem: execution-client-gas-accounting
bug_class: delegatecall-surcharge-identity-mismatch
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-19 Custom gas penalty should not be applied to delegatecall (and deprecated callcode) (#48)
impact_type:
  - "fee-miscalculation"
  - "denial-of-service"
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

Custom gas penalty should not be applied to delegatecall and callcode is a report-derived Blast finding from the 2024 competition. The reusable issue is: Custom first-use gas penalties should use the same identity for surcharge admission and fee allocation under delegatecall/callcode semantics.

## Root Cause

The high-frame surcharge checks whether the target library address has allocation, but delegatecall/callcode execution and gas attribution use the caller context.

## Attack Surface

- Trust boundary: CALL-family opcode gas calculation -> GasTracker allocation
- Entrypoint: DELEGATECALL or CALLCODE after frame threshold
- Sensitive sink: caller-context gas allocation and custom surcharge

## Preconditions And Capabilities

- Attacker capability: execute deep proxy/library call patterns or induce victim-paid delegatecall loops
- Preconditions: surcharge predicate checks target code address
- Preconditions: gas is charged to caller/storage context and target remains unallocated

## Impact

Impact types: fee-miscalculation, denial-of-service, compatibility-break. Blast radius: proxy/library patterns and sponsored transactions.

## Patch Pattern

For delegatecall/callcode, key the surcharge predicate to the allocation address or suppress target-first-use penalties that cannot create target allocation.

## Source References

- report.md#M-19
- operations_acl.go
- evm.go DelegateCall
- contract.go UseGasNatively
