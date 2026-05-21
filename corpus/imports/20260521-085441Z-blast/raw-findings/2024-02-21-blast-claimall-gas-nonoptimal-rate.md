---
case_id: m_04_claimall_gas_nonoptimal_rate
project: blast
domain: blockchain-core
subsystem: gas-claim-predeploy
bug_class: claim-helper-nonoptimal-payout
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-04 claimAll() function may not claim gas at optimal rate (#1014)
impact_type:
  - "fee-bypass"
  - "value-miscalculation"
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

claimAll function may not claim gas at optimal rate is a report-derived Blast finding from the 2024 competition. The reusable issue is: Convenience claim helpers should not force a lower payout than an equivalent sequence of allowed split claims over the same balance and maturity state.

## Root Cause

The helper drains all gas using one rate calculation, while lower-level claims can split amount/seconds to obtain a better effective rate.

## Attack Surface

- Trust boundary: authorized gas governor -> Gas predeploy claim curve
- Entrypoint: claimAllGas or claimMaxGas helper
- Sensitive sink: claimable gas payout and retained seconds accounting

## Preconditions And Capabilities

- Attacker capability: control or govern a contract with claimable gas
- Attacker capability: choose claim helper and claim timing
- Preconditions: claim curve has base/ceil regions
- Preconditions: partial claims can preserve maturity more efficiently than a one-shot helper

## Impact

Impact types: fee-bypass, value-miscalculation. Blast radius: claimable gas owners and fee vault penalties.

## Patch Pattern

Make claimAll compute the optimal payout over the claim curve or document it as non-optimal and expose safe helper semantics.

## Source References

- report.md#M-04
- Gas.sol::claimAll
- Gas.sol::claimGasAtMinClaimRate
