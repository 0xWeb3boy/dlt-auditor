---
case_id: m_20_upgrade_reinitializer_double_withdrawal
project: blast
domain: blockchain-core
subsystem: cross-domain-messenger-upgrades
bug_class: upgrade-reinitializer-reentrancy-reset
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-20 Anyone can front-run upgrades to execute a double withdrawal (#12)
impact_type:
  - "double-withdrawal"
  - "asset-drain"
  - "cross-domain-replay"
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

Anyone can front-run upgrades to execute a double withdrawal is a report-derived Blast finding from the 2024 competition. The reusable issue is: Upgrade initializers must not reset active reentrancy/replay guard state while a failed value-bearing message retry is executing.

## Root Cause

relayMessage sets xDomainMsgSender before the external call and marks success afterward; a reinitializer can reset the guard mid-call, allowing nested replay before success is recorded.

## Attack Surface

- Trust boundary: governance upgrade transaction -> active cross-domain message relay
- Entrypoint: failed value-bearing relay target that executes signed upgrade and reenters relayMessage
- Sensitive sink: xDomainMsgSender guard and successfulMessages/failedMessages maps

## Preconditions And Capabilities

- Attacker capability: observe a signed upgrade transaction
- Attacker capability: front-run it inside a failed value-bearing withdrawal payload
- Attacker capability: reenter relayMessage from the target callback
- Preconditions: failedMessages is already true for the message
- Preconditions: initializer resets xDomainMsgSender during the callback
- Preconditions: successfulMessages is not rechecked after the external call

## Impact

Impact types: double-withdrawal, asset-drain, cross-domain-replay. Blast radius: L1 messenger ETH balance and failed value messages.

## Patch Pattern

Do not reset active relay guards in upgrade initializers, and recheck successfulMessages or active relay state after the external target call returns.

## Source References

- report.md#M-20
- CrossDomainMessenger.sol
- L1CrossDomainMessenger.sol
- ProxyAdmin.upgradeAndCall
