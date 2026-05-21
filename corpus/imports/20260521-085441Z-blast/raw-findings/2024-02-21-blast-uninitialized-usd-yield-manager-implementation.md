---
case_id: h_04_uninitialized_usd_yield_manager_implementation
project: blast
domain: blockchain-core
subsystem: yield-manager-upgradeability
bug_class: unlocked-proxy-implementation-initializer
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: H-04 USD Yield Manager can be bricked by self destructing uninitialized implementation (#1036)
impact_type:
  - "denial-of-service"
  - "upgrade-safety"
  - "unauthorized-action"
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

USD Yield Manager can be bricked by self destructing uninitialized implementation is a report-derived Blast finding from the 2024 competition. The reusable issue is: Implementation contracts behind proxies must not remain publicly initializable when initialization grants ownership or reaches delegatecall hooks.

## Root Cause

ETHYieldManager locks its implementation in the constructor, while USDYieldManager leaves the Initializable path open; owner-only addProvider can delegatecall attacker-controlled provider code.

## Attack Surface

- Trust boundary: external caller -> implementation contract address
- Entrypoint: direct initialize call on implementation
- Sensitive sink: owner-only provider registration and delegatecall to provider code

## Preconditions And Capabilities

- Attacker capability: call the implementation address directly before it is locked
- Attacker capability: deploy provider code bound to the implementation address
- Preconditions: implementation initializer is unconsumed
- Preconditions: provider initialization or destructive code executes in implementation context

## Impact

Impact types: denial-of-service, upgrade-safety, unauthorized-action. Blast radius: implementation availability and deployment safety.

## Patch Pattern

Lock implementation initializers in constructors and avoid exposing implementation-local ownership paths that can reach delegatecall-capable plugins.

## Source References

- report.md#H-04
- USDYieldManager.sol
- ETHYieldManager.sol
- YieldManager.sol::addProvider
