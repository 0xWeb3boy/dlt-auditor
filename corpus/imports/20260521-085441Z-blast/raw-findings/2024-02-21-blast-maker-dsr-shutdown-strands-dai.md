---
case_id: m_17_maker_dsr_shutdown_strands_dai
project: blast
domain: blockchain-core
subsystem: usd-yield-provider
bug_class: external-provider-shutdown-recovery-gap
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-17 All staked DAI will be permanently lost if Maker initiates the Shutdown Mechanism (#527)
impact_type:
  - "asset-stranding"
  - "liveness-failure"
  - "staking-recovery-failure"
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

All staked DAI will be permanently lost if Maker initiates the Shutdown Mechanism is a report-derived Blast finding from the 2024 competition. The reusable issue is: External staking-provider integration must support the provider shutdown/recovery mechanism for assets whose normal manager wrapper can no longer exit.

## Root Cause

The provider uses DSR_MANAGER.join/exit and values pieOf as recoverable, but lacks an alternate End.sol/Pot/DaiJoin shutdown recovery route.

## Attack Surface

- Trust boundary: Maker emergency shutdown -> Blast USD yield accounting
- Entrypoint: DSRYieldProvider unstake or premium path after Maker cage/shutdown
- Sensitive sink: DSR_MANAGER.exit and DAI recovery ownership

## Preconditions And Capabilities

- Attacker capability: no attacker required beyond Maker shutdown; users/operators later need withdrawals or recovery
- Preconditions: Blast has DAI staked through DSR_MANAGER
- Preconditions: Maker disables normal exit or requires End.sol recovery outside DSR_MANAGER

## Impact

Impact types: asset-stranding, liveness-failure, staking-recovery-failure. Blast radius: USD yield manager DAI backing.

## Patch Pattern

Integrate directly with Maker shutdown redemption flows or add an audited emergency recovery path that can recover DAI when DSR_MANAGER exit is unavailable.

## Source References

- report.md#M-17
- DSRYieldProvider.sol
- Maker DSR_MANAGER
