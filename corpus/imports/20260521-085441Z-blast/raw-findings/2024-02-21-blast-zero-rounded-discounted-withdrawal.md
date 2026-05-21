---
case_id: m_03_zero_rounded_discounted_withdrawal
project: blast
domain: blockchain-core
subsystem: bridge-withdrawal-discounting
bug_class: zero-rounded-positive-value-lifecycle
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-03 Withdrawals that include 1 wei will be bricked in the event of a negative rebase (#1031)
impact_type:
  - "asset-stranding"
  - "cross-domain-lifecycle-failure"
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

Withdrawals that include 1 wei can be bricked in negative rebase is a report-derived Blast finding from the 2024 competition. The reusable issue is: A positive nominal withdrawal whose discounted value rounds to zero should be rejected before consuming state or recorded as replayable failure.

## Root Cause

The withdrawal queue allows realAmount == 0 for a positive nominal request; messenger first-submission assertions then fail before writing retry state.

## Attack Surface

- Trust boundary: discounted yield withdrawal -> cross-domain messenger replay state
- Entrypoint: positive-value L2-to-L1 withdrawal during negative yield
- Sensitive sink: portal finalizedWithdrawals and messenger failedMessages/discountedValues

## Preconditions And Capabilities

- Attacker capability: create a dust positive-value withdrawal while share price is below par
- Preconditions: nominal amount times share price floors to zero
- Preconditions: portal/yield state is consumed before messenger records failure

## Impact

Impact types: asset-stranding, cross-domain-lifecycle-failure. Blast radius: dust or low-value discounted withdrawals unless share price collapse is severe.

## Patch Pattern

Reject positive nominal claims that discount to zero before finalization, or teach messenger/portal replay state to represent zero-rounded positive messages.

## Source References

- report.md#M-03
- WithdrawalQueue.sol
- OptimismPortal.sol
- L1CrossDomainMessenger.sol
