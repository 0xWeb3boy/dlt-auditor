---
case_id: h_02_socialized_gas_refunds_dev_fee_theft
project: blast
domain: blockchain-core
subsystem: gas-fee-attribution
bug_class: global-refund-socialization
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: H-02 Users can steal 20% of all gas fees back from developers due to imprecise refund mechanism (#1083)
impact_type:
  - "fee-bypass"
  - "unauthorized-value-shift"
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

Users can steal gas fees back from developers due to imprecise refund mechanism is a report-derived Blast finding from the 2024 competition. The reusable issue is: Gas refunds should reduce the claimable allocation of the contract that generated the refund, not proportionally reduce unrelated contracts touched in the same transaction.

## Root Cause

GasTracker scales every allocation by (gasUsed - refund) / gasUsed using a transaction-global refund number, losing which contract caused the refund.

## Attack Surface

- Trust boundary: user-controlled EVM execution -> developer gas-fee distribution
- Entrypoint: post-transaction GasTracker allocation
- Sensitive sink: per-contract claimable gas accounting

## Preconditions And Capabilities

- Attacker capability: execute a transaction that touches victim contracts and an attacker-controlled refunding contract
- Attacker capability: pre-seed refundable storage or otherwise generate EVM refunds
- Preconditions: the transaction contains both victim gas use and attacker-generated refunds
- Preconditions: refunds are represented as one global transaction counter

## Impact

Impact types: fee-bypass, unauthorized-value-shift, resource-accounting. Blast radius: application and protocol fee accounting.

## Patch Pattern

Avoid user-controlled gas refunds in the accounting model or track refund source precisely enough that refunds only reduce the generating contract allocation.

## Source References

- report.md#H-02
- blast-geth/core/vm/gas_tracker.go::AllocateDevGas
