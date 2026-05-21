---
case_id: m_05_protocol_fee_vault_discounted_withdrawal
project: blast
domain: blockchain-core
subsystem: fee-vault-withdrawals
bug_class: fee-vault-discount-domain-mismatch
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-05 Blast can be forced to withdraw protocol gas fees at a discount in negative yield event (#1005)
impact_type:
  - "fee-bypass"
  - "protocol-revenue-loss"
  - "accounting-invariant-break"
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

Blast can be forced to withdraw protocol gas fees at a discount in negative yield event is a report-derived Blast finding from the 2024 competition. The reusable issue is: Protocol fee buckets collected for sequencer/base/L1 cost recovery should not silently share user yield-provider losses unless that policy is explicit.

## Root Cause

Fee vault balances are nominal protocol fees on L2 but are withdrawn through the same discounted user ETH queue used for yield losses.

## Attack Surface

- Trust boundary: permissionless L2 fee-vault withdrawal -> L1 discounted ETH settlement
- Entrypoint: FeeVault.withdraw during negative yield
- Sensitive sink: OptimismPortal discounted ETH withdrawal claim

## Preconditions And Capabilities

- Attacker capability: call permissionless fee-vault withdrawal when threshold and negative-yield state exist
- Preconditions: fee vault remote withdrawal goes through the generic discounted ETH path
- Preconditions: share price is below par at finalization

## Impact

Impact types: fee-bypass, protocol-revenue-loss, accounting-invariant-break. Blast radius: protocol fee recipients and remaining ETH holders.

## Patch Pattern

Route protocol fee vaults through nominal-value settlement or explicitly account/document their participation in negative-yield socialization.

## Source References

- report.md#M-05
- FeeVault.sol
- OptimismPortal.sol
- YieldManager.sol
