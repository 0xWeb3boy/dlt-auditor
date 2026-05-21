---
case_id: m_13_l1_da_fee_undercharge_discounted_withdrawal
project: blast
domain: blockchain-core
subsystem: fee-vault-accounting
bug_class: fee-recovery-discount-mismatch
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-13 DoS due to Undercharging L1 Data Availability Fees on L2 During Discounted WIthdrawals (#765)
impact_type:
  - "fee-bypass"
  - "protocol-cost-underrecovery"
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

Undercharging L1 data availability fees on L2 during discounted withdrawals is a report-derived Blast finding from the 2024 competition. The reusable issue is: Fees charged to recover L1 data availability costs should settle to the L1 fee recipient at the nominal amount unless a discount policy is explicit.

## Root Cause

The same discounted withdrawal mechanism used for user ETH is applied to fee vault balances collected for L1 data costs.

## Attack Surface

- Trust boundary: L2 L1/DA fee accounting -> L1 fee recipient withdrawal
- Entrypoint: L1FeeVault withdrawal during negative yield
- Sensitive sink: remote fee-vault payout through discounted withdrawal path

## Preconditions And Capabilities

- Attacker capability: trigger permissionless fee-vault withdrawal when negative-yield discount exists
- Preconditions: L1FeeVault uses generic ETH withdrawal path
- Preconditions: share price is below par when checkpointed

## Impact

Impact types: fee-bypass, protocol-cost-underrecovery, resource-accounting. Blast radius: protocol operator cost recovery.

## Patch Pattern

Separate fee-vault settlement from user yield-discount settlement or account the discount explicitly in fee charging.

## Source References

- report.md#M-13
- FeeVault.sol
- OptimismPortal.sol
