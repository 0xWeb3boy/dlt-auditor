---
case_id: h_03_direct_eth_yield_deposit_min_gas_bricking
project: blast
domain: blockchain-core
subsystem: bridge
bug_class: bridge-direct-deposit-gas-budget
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: H-03 minGasLimit miscalculated for stETH deposits, leading to bricked funds (#1077)
impact_type:
  - "asset-stranding"
  - "denial-of-service"
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

minGasLimit miscalculated for stETH deposits leading to bricked funds is a report-derived Blast finding from the 2024 competition. The reusable issue is: Direct bridge deposits that bypass the messenger must still budget enough gas for finalization or provide an equivalent replay/refund path.

## Root Cause

A direct deposit path sends portal value and finalizer calldata with user-provided minGasLimit, but the L2 finalizer has no messenger failed-message state or replay handle.

## Attack Surface

- Trust boundary: L1 bridge deposit -> L2 value finalization
- Entrypoint: L1 ETH-yield-token bridgeERC20/bridgeERC20To
- Sensitive sink: L2 direct ETH finalizer and recipient transfer

## Preconditions And Capabilities

- Attacker capability: submit or induce a direct ETH-yield-token bridge deposit
- Attacker capability: choose a low minGasLimit or recipient behavior that makes finalization fail
- Preconditions: deposit uses the direct portal path rather than normal messenger retry semantics
- Preconditions: finalization failure occurs after L1-side custody/accounting changes

## Impact

Impact types: asset-stranding, denial-of-service, cross-domain-lifecycle-failure. Blast radius: bridge-domain to settlement-domain.

## Patch Pattern

Compute a mandatory base gas floor for the direct finalizer or route value-bearing deposits through a replayable messenger path.

## Source References

- report.md#H-03
- L1BlastBridge.sol
- L2BlastBridge.sol
