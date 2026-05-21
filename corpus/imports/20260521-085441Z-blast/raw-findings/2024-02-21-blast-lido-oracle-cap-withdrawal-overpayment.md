---
case_id: m_11_lido_oracle_cap_withdrawal_overpayment
project: blast
domain: blockchain-core
subsystem: yield-provider-accounting
bug_class: external-oracle-loss-lag
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-11 Insolvency due to Overpayment For Withdrawals in Slashing Events Exceeding 5% (#783)
impact_type:
  - "insolvency-risk"
  - "value-transfer-between-cohorts"
  - "stale-trust-state"
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

Overpayment for withdrawals in slashing events exceeding oracle cap is a report-derived Blast finding from the 2024 competition. The reusable issue is: External provider losses that are known or pending must be reflected before withdrawal checkpoints can pay exiting users at par.

## Root Cause

Share price depends on provider totalValue and accumulatedNegativeYields, but Lido losses are only realized after oracle/report/claim sequencing.

## Attack Surface

- Trust boundary: Lido oracle/provider truth -> Blast withdrawal settlement
- Entrypoint: YieldManager.finalize during oracle-cap or delayed-loss window
- Sensitive sink: withdrawal checkpoint share price and payout amount

## Preconditions And Capabilities

- Attacker capability: time a withdrawal before operators report/claim the full Lido loss
- Preconditions: Lido loss exceeds reporting cap or is delayed from Blast accounting
- Preconditions: withdrawal finalization uses stale share price

## Impact

Impact types: insolvency-risk, value-transfer-between-cohorts, stale-trust-state. Blast radius: ETH yield manager and remaining ETH holders.

## Patch Pattern

Require fresh provider loss reporting/claiming before finalization, especially around oracle-capped or delayed-loss windows.

## Source References

- report.md#M-11
- YieldManager.sol::sharePrice
- LidoYieldProvider.sol
