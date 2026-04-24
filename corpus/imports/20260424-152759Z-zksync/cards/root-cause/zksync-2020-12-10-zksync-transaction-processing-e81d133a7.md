# Root-Cause Card

## Metadata

- ID: `zksync-2020-12-10-zksync-transaction-processing-e81d133a7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insecure-default-secret-detection`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `production-secret-safety-check`

## Violated Invariant

- Invariant: Non-local deployments must not silently run privileged admin or prover authentication with documented sample secrets.

## Trust Boundary

- Boundary: Deployment configuration crosses into authentication secret material for privileged services.

## Attack Surface

- Entrypoint type: `configuration_loading_and_startup`
- Sensitive sink: admin server and prover API shared-secret authentication

## Impact Pattern

- Primary impact: misconfiguration leading to predictable shared-secret auth
- Secondary impact: operator alerting for unsafe production defaults

## Short Reusable Lesson

- Configuration loading now detects sample admin/prover auth secrets outside localhost and emits explicit errors. The reusable shape is deployment config accepting known default credentials for privileged services without environment-sensitive safety checks.
