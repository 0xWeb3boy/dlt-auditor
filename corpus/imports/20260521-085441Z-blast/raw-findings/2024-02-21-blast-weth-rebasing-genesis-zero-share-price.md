---
case_id: h_06_weth_rebasing_genesis_zero_share_price
project: blast
domain: blockchain-core
subsystem: l2-genesis-predeploys
bug_class: initializer-genesis-state-mismatch
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: H-06 WETH will never rebase because the initial share price and share count of WETHRebasing is 0. (#109)
impact_type:
  - "state-integrity"
  - "asset-yield-loss"
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

WETH will never rebase because initial share price and share count are zero is a report-derived Blast finding from the 2024 competition. The reusable issue is: Genesis storage for initialized proxied predeploys must include all storage postconditions of the initializer, especially accounting price and share state.

## Root Cause

Direct genesis storage sets initialized flags and native yield mode, but does not seed the WETH rebasing token price that normal initialize would set from Shares.price.

## Attack Surface

- Trust boundary: genesis builder -> live L2 predeploy state
- Entrypoint: L2 genesis construction
- Sensitive sink: WETHRebasing ERC20 share-price and total-share accounting

## Preconditions And Capabilities

- Attacker capability: no attacker needed; any user later deposits into the affected WETH predeploy
- Preconditions: genesis marks initializer consumed while omitting price/share accounting fields
- Preconditions: normal initializer cannot run after launch

## Impact

Impact types: state-integrity, asset-yield-loss, lifecycle-invariant-break. Blast radius: chain-wide WETH predeploy accounting.

## Patch Pattern

Execute the initializer during genesis or write every initializer-equivalent storage field, including price, metadata, and Blast config.

## Source References

- report.md#H-06
- op-chain-ops/genesis/config.go
- WETHRebasing.sol
- ERC20Rebasing.sol
