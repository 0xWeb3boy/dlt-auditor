---
case_id: h_08_subclaimableamount_journal_prevflags
project: blast
domain: blockchain-core
subsystem: execution-client-state-journal
bug_class: incomplete-journal-rollback
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: H-08 Journal entry is missing flag parameter in SubClaimableAmount which can cause account type switch to YieldAutomatic (#10)
impact_type:
  - "state-integrity"
  - "unauthorized-value-shift"
  - "lifecycle-invariant-break"
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

Journal entry is missing flag parameter in SubClaimableAmount is a report-derived Blast finding from the 2024 competition. The reusable issue is: Every journal entry that mutates an account yield representation must restore flags, fixed balance, shares, and remainder together on revert.

## Root Cause

SubClaimableAmount journals fixed/shares/remainder but omits prevFlags; rollback writes the zero-value flag, switching the account to YieldAutomatic.

## Attack Surface

- Trust boundary: authorized yield claim -> EVM revert journal
- Entrypoint: Blast claimYield/claimAllYield through native precompile
- Sensitive sink: StateDB balanceValuesChange rollback

## Preconditions And Capabilities

- Attacker capability: trigger an authorized nonzero claim and then cause the enclosing frame to revert
- Preconditions: account is YieldClaimable
- Preconditions: SubClaimableAmount succeeds before a later revert

## Impact

Impact types: state-integrity, unauthorized-value-shift, lifecycle-invariant-break. Blast radius: affected claimable-yield accounts.

## Patch Pattern

Include previous flags in every balance/yield journal entry and add revert-after-success tests for claimable yield operations.

## Source References

- report.md#H-08
- blast-geth/core/state/state_object.go
- blast-geth/core/state/journal.go
