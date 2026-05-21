---
case_id: h_01_saved_etherseconds_gas_refund_dos
project: blast
domain: blockchain-core
subsystem: gas-refund-accounting
bug_class: gas-refund-maturity-reuse
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: H-01 etherSeconds can be accrued to allow riskless DOS of the node (#1101)
impact_type:
  - "denial-of-service"
  - "fee-bypass"
  - "resource-accounting"
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

etherSeconds can be accrued to allow riskless DOS of the node is a report-derived Blast finding from the 2024 competition. The reusable issue is: Gas refund maturity should be consumed when the corresponding gas balance is claimed so old seconds cannot subsidize future block-stuffing work.

## Root Cause

Gas accounting stores claimable gas value and maturity seconds separately; a full-balance claim consumes only the seconds needed for the selected payout rate and can leave reusable maturity behind.

## Attack Surface

- Trust boundary: user transaction -> Blast gas-refund accounting
- Entrypoint: gas-claim path and post-transaction gas allocation
- Sensitive sink: Gas predeploy etherBalance and etherSeconds state

## Preconditions And Capabilities

- Attacker capability: control a contract or governor that accrues claimable gas
- Attacker capability: submit gas-heavy transactions and time gas claims
- Preconditions: gas refunds mature faster than the attack capital is exhausted
- Preconditions: claim paths can drain etherBalance while leaving surplus etherSeconds

## Impact

Impact types: denial-of-service, fee-bypass, resource-accounting. Blast radius: chain-wide resource pressure.

## Patch Pattern

When claimable gas balance is fully withdrawn, clear or cap the associated maturity seconds so old seconds cannot apply to newly accrued gas.

## Source References

- report.md#H-01
- blast-optimism/packages/contracts-bedrock/src/L2/Gas.sol
- blast-geth/core/vm/gas_tracker.go
