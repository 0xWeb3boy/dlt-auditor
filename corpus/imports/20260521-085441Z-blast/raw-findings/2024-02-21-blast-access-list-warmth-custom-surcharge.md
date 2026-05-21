---
case_id: m_07_access_list_warmth_custom_surcharge
project: blast
domain: blockchain-core
subsystem: execution-client-gas-accounting
bug_class: access-list-custom-gas-incompatibility
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-07 EVM-incompatibility: EIP-2930 which mitigates risks of EIP-2929, could possibly break for some contracts (#841)
impact_type:
  - "compatibility-break"
  - "denial-of-service"
  - "gas-accounting"
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

EIP-2930 access lists could break for some contracts is a report-derived Blast finding from the 2024 competition. The reusable issue is: If an access list prewarms a target for EVM gas semantics, Blast-specific custom gas should not reintroduce an unpriced cold-style failure mode for the same target class.

## Root Cause

The standard cold-account cost respects access-list warmth, but the Blast high-frame surcharge ignores that warmth and can still add storage-style gas.

## Attack Surface

- Trust boundary: transaction access list -> CALL-family gas calculation
- Entrypoint: EIP-2930 or EIP-1559 transaction with access list
- Sensitive sink: CALL dynamic gas and OOG behavior

## Preconditions And Capabilities

- Attacker capability: submit transactions with access lists or rely on relayer-generated access lists
- Preconditions: call path crosses Blast high-frame threshold
- Preconditions: contract assumes prewarmed access will fit a gas budget

## Impact

Impact types: compatibility-break, denial-of-service, gas-accounting. Blast radius: applications relying on access-list gas guarantees.

## Patch Pattern

Integrate access-list warmth into the custom surcharge or expose/document a separate gas rule that callers can estimate reliably.

## Source References

- report.md#M-07
- operations_acl.go
- state_transition.go access list
