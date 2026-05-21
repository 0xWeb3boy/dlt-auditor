---
case_id: m_16_insurance_fresh_steth_front_run
project: blast
domain: blockchain-core
subsystem: yield-provider-insurance
bug_class: loss-eligibility-snapshot-gap
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-16 The one time insurance will need to work, it won't (#545)
impact_type:
  - "value-transfer-between-cohorts"
  - "insurance-drain"
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

The one time insurance will need to work, it won't is a report-derived Blast finding from the 2024 competition. The reusable issue is: Insurance or recovery for an externally known provider loss should apply to holders exposed at loss time, not fresh entrants who deposit after observing the loss.

## Root Cause

Bridge deposits mint L2 ETH or provider principal at stale/par value, while the later insurance/report path repairs the aggregate pool rather than only pre-loss holders.

## Attack Surface

- Trust boundary: external provider impairment -> bridge deposit and insurance accounting
- Entrypoint: fresh stETH deposit before loss report/insurance repair
- Sensitive sink: ETH yield manager share minting and insurance repair distribution

## Preconditions And Capabilities

- Attacker capability: observe or predict a Lido loss before Blast reports it
- Attacker capability: deposit stETH while admission remains open
- Preconditions: loss is externally knowable but not yet reflected in Blast share price
- Preconditions: insurance repair is socialized across current balances

## Impact

Impact types: value-transfer-between-cohorts, insurance-drain, stale-trust-state. Blast radius: ETH yield manager holders and insurance pool.

## Patch Pattern

Pause or discount fresh deposits during known provider-loss windows and bind insurance eligibility to pre-loss accounting snapshots.

## Source References

- report.md#M-16
- L1BlastBridge.sol
- YieldManager.sol
- LidoYieldProvider.sol
