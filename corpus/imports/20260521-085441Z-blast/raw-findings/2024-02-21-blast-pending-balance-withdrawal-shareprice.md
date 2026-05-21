---
case_id: m_09_pending_balance_withdrawal_shareprice
project: blast
domain: blockchain-core
subsystem: yield-provider-accounting
bug_class: stale-provider-loss-checkpoint
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-09 Insolvency due to Inclusion of pendingBalance Funds in Withdrawal sharePrice Calculation (#795)
impact_type:
  - "insolvency-risk"
  - "value-transfer-between-cohorts"
  - "state-integrity"
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

PendingBalance funds included in withdrawal sharePrice calculation is a report-derived Blast finding from the 2024 competition. The reusable issue is: Withdrawal checkpoints should not price pending or claimable provider exits at par when their realized value is already knowable and below nominal.

## Root Cause

Provider totalValue includes pendingBalance at nominal value, while realized negative yield is only recorded when claim/report hooks process exits.

## Attack Surface

- Trust boundary: external yield provider state -> L1 withdrawal queue checkpoint
- Entrypoint: YieldManager.finalize before Lido claim/report catches up
- Sensitive sink: WithdrawalQueue finalized checkpoint share price

## Preconditions And Capabilities

- Attacker capability: time withdrawals around provider exit finalization and admin/keeper sequencing
- Preconditions: pending Lido exits are claimable below nominal
- Preconditions: finalize runs before all losses are claimed/reported

## Impact

Impact types: insolvency-risk, value-transfer-between-cohorts, state-integrity. Blast radius: ETH yield manager withdrawal cohorts.

## Patch Pattern

Before finalizing withdrawals, force provider claim/report freshness or block finalization while claimable below-par exits remain unprocessed.

## Source References

- report.md#M-09
- YieldManager.sol::finalize
- LidoYieldProvider.sol
- WithdrawalQueue.sol
