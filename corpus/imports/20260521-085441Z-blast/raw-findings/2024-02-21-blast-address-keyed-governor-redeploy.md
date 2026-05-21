---
case_id: m_02_address_keyed_governor_redeploy
project: blast
domain: blockchain-core
subsystem: l2-predeploy-configuration
bug_class: durable-address-keyed-configuration
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-02 CREATE2 deployments can have governor role stolen (#1091)
impact_type:
  - "unauthorized-action"
  - "fee-claim-theft"
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

CREATE2 deployments can have governor role stolen is a report-derived Blast finding from the 2024 competition. The reusable issue is: Gas/yield governor state that grants rights over a contract should be bound to the intended code identity or cleared/rebound across destructive lifecycle and redeploy events.

## Root Cause

Blast authorization is keyed by address only; create/redeploy/proxy lifecycle can change code while governor and gas/yield state persist outside the contract storage.

## Attack Surface

- Trust boundary: contract address lifecycle -> Blast gas/yield governance
- Entrypoint: CREATE2/metamorphic deployment or proxy/redeploy lifecycle
- Sensitive sink: Blast.governorMap and Gas per-address configuration

## Preconditions And Capabilities

- Attacker capability: preconfigure or retain governor rights for an address whose code identity later changes
- Preconditions: a later contract is deployed or upgraded at the same configured address
- Preconditions: old address-keyed state remains authoritative

## Impact

Impact types: unauthorized-action, fee-claim-theft, stale-trust-state. Blast radius: affected contracts and governors.

## Patch Pattern

Clear/rebind external gas/yield config on code identity changes or require deployments to opt into durable address-lifetime ownership explicitly.

## Source References

- report.md#M-02
- Blast.sol::governorMap
- Gas.sol
