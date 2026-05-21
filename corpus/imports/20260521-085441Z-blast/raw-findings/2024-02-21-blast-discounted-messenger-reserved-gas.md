---
case_id: h_07_discounted_messenger_reserved_gas
project: blast
domain: blockchain-core
subsystem: cross-domain-messenger
bug_class: bridge-failure-record-gas-underreserve
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: H-07 Withdrawals/messages can be lost due to incorrect RELAY_RESERVED_GAS value in L1CrossDomainMessenger (#19)
impact_type:
  - "asset-stranding"
  - "cross-domain-lifecycle-failure"
  - "denial-of-service"
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

Withdrawals/messages can be lost due to incorrect RELAY_RESERVED_GAS value is a report-derived Blast finding from the 2024 competition. The reusable issue is: Portal finalization must not become permanent unless messenger success or replayable failure state, including discounted value sidecars, can be durably recorded within the reserved gas.

## Root Cause

Messenger reserve gas was inherited from a path with fewer writes; Blast added discountedValues persistence on failure without increasing the relay reserve.

## Attack Surface

- Trust boundary: L2-to-L1 message finalization -> L1 messenger failure state
- Entrypoint: OptimismPortal.finalizeWithdrawalTransaction targeting L1CrossDomainMessenger
- Sensitive sink: failedMessages and discountedValues storage writes

## Preconditions And Capabilities

- Attacker capability: create a value-bearing withdrawal whose target fails after consuming most forwarded gas
- Preconditions: portal marks withdrawal finalized before the target call
- Preconditions: messenger failure path needs additional Blast discounted-value storage writes

## Impact

Impact types: asset-stranding, cross-domain-lifecycle-failure, denial-of-service. Blast radius: bridge-domain to settlement-domain.

## Patch Pattern

Increase reserved gas or restructure finalization so failure replay state is written before value/lifecycle state is consumed.

## Source References

- report.md#H-07
- L1CrossDomainMessenger.sol
- OptimismPortal.sol
