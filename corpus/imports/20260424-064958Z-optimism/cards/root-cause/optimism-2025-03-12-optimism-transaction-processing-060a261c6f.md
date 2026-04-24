# Root-Cause Card

## Metadata

- ID: `optimism-2025-03-12-optimism-transaction-processing-060a261c6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-scoping`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `configuration-validation`

## Violated Invariant

- Invariant: A deployment should not be routed onto the shared predeployed OPCM and global SuperchainConfig path solely because tagged artifacts exist; that path should be used only for intents that explicitly match the standard configuration and standard governance-role assumptions.

## Trust Boundary

- Boundary: operator configuration -> deployment/genesis artifacts

## Attack Surface

- Entrypoint type: configuration-loader or deployment pipeline
- Sensitive sink: generation or activation of privileged protocol configuration

## Impact Pattern

- Primary impact: governance-misconfiguration
- Secondary impact: configuration-safety

## Short Reusable Lesson

- A deployment should not be routed onto the shared predeployed OPCM and global SuperchainConfig path solely because tagged artifacts exist; that path should be used only for intents that explicitly match the standard configuration and standard governance-role assumptions. Similar bugs appear when configuration-loader or deployment pipeline code treats partially checked input as authoritative and lets it reach generation or activation of privileged protocol configuration. The reusable fix is to enforce configuration-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
