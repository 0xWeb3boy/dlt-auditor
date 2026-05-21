---
case_id: m_12_eth_yield_token_decimal_conversion
project: blast
domain: blockchain-core
subsystem: bridge
bug_class: cross-domain-unit-conversion-mismatch
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-12 SpearBit's 5.3.2 Unaddressed: L1BlastBridge directly sends _amount of ETH without converting to 18 decimals (#775)
impact_type:
  - "asset-stranding"
  - "cross-domain-accounting-error"
  - "input-validation"
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

L1BlastBridge directly sends _amount of ETH without converting to 18 decimals is a report-derived Blast finding from the 2024 competition. The reusable issue is: The value sent through a portal and the amount encoded for the L2 finalizer must use the same decimal unit and equality expectation.

## Root Cause

One branch converts token amount to 18 decimals for finalizer calldata while another uses raw token units as portal ETH value.

## Attack Surface

- Trust boundary: L1 ERC20 deposit amount -> L2 native ETH finalizer
- Entrypoint: bridgeERC20To with approved non-18-decimal ETH-yield token
- Sensitive sink: portal msg.value and L2 finalizeBridgeETHDirect equality check

## Preconditions And Capabilities

- Attacker capability: deposit an approved ETH-yield token whose decimals differ from 18
- Preconditions: governance approves a non-18-decimal ETH-yield token
- Preconditions: bridge path uses raw amount for value and WAD amount for calldata/accounting

## Impact

Impact types: asset-stranding, cross-domain-accounting-error, input-validation. Blast radius: bridge deposits for non-18-decimal yield assets.

## Patch Pattern

Normalize units once at the boundary and use the same normalized amount for custody, portal value, finalizer calldata, and provider accounting.

## Source References

- report.md#M-12
- L1BlastBridge.sol
- L2BlastBridge.sol
