---
case_id: m_10_nonupgradeable_predeploys_proxied
project: blast
domain: blockchain-core
subsystem: l2-genesis-predeploys
bug_class: constructor-only-contract-behind-proxy
source_quality: high
date: 2024-02-21
source_report: /testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md
source_report_heading: M-10 Non-upgradeable predeploys are deployed behind upgradeable proxies (#786)
impact_type:
  - "upgrade-safety"
  - "unauthorized-action"
  - "state-integrity"
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

Non-upgradeable predeploys are deployed behind upgradeable proxies is a report-derived Blast finding from the 2024 competition. The reusable issue is: Contracts intended to rely on constructor-only invariants should either not be proxied or should provide initializer/reinitializer paths and tests for every proxy upgrade scenario.

## Root Cause

Predeploy proxy rules include Blast and Gas even though their security-relevant setup is constructor-oriented and not expressed as upgradeable Initializable storage.

## Attack Surface

- Trust boundary: genesis/deployment proxy admin -> system predeploy logic
- Entrypoint: L2 predeploy proxy installation and future ProxyAdmin upgrade
- Sensitive sink: Blast and Gas predeploy implementation and mutable configuration

## Preconditions And Capabilities

- Attacker capability: control or compromise the proxy admin, or rely on future upgrades that bypass constructor validation
- Preconditions: constructor-only Blast/Gas contracts are treated as proxied system contracts
- Preconditions: upgrade authority can swap logic without constructor parity

## Impact

Impact types: upgrade-safety, unauthorized-action, state-integrity. Blast radius: chain-wide system predeploys.

## Patch Pattern

Mark constructor-only predeploys as non-proxied, or convert them to explicit upgradeable contracts with initializer parity and upgrade tests.

## Source References

- report.md#M-10
- op-bindings/predeploys/addresses.go::IsProxied
- Gas.sol
- Blast.sol
