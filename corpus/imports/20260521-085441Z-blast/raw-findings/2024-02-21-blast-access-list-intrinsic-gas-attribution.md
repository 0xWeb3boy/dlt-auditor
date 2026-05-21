---
case_id: m_14_access_list_intrinsic_gas_attribution
project: blast
domain: blockchain-core
subsystem: gas-fee-attribution
bug_class: intrinsic-gas-attribution-mismatch
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-14 Access lists attribute gas to Blast instead of the smart contracts that induce them (#641)
impact_type:
  - "fee-attribution-error"
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

Access lists attribute gas to Blast instead of the smart contracts that induce them is a report-derived Blast finding from the 2024 competition. The reusable issue is: Access-list intrinsic gas paid to warm contract/storage accesses should be attributed to the contract or surface that benefits from the warmed access, not a global bucket.

## Root Cause

Intrinsic access-list gas is allocated to a global Blast gas address; the later warmed contract receives lower opcode gas and no corresponding intrinsic allocation.

## Attack Surface

- Trust boundary: transaction intrinsic gas -> developer gas accounting
- Entrypoint: EIP-2930 access list transaction
- Sensitive sink: GasTracker allocation and claimable gas recipient

## Preconditions And Capabilities

- Attacker capability: submit transactions with access lists touching target contracts
- Preconditions: access-list intrinsic gas is charged before warmed accesses execute
- Preconditions: allocation credits the global Blast address rather than target contract

## Impact

Impact types: fee-attribution-error, fee-bypass. Blast radius: developer gas revenue and protocol fee bucket.

## Patch Pattern

Attribute access-list intrinsic costs to the warmed targets or make access-list costs non-claimable by design with explicit accounting.

## Source References

- report.md#M-14
- state_transition.go intrinsic gas
- GasTracker
