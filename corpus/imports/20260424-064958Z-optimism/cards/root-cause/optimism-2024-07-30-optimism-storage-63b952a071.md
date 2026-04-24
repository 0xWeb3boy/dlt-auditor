# Root-Cause Card

## Metadata

- ID: `optimism-2024-07-30-optimism-storage-63b952a071`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `configuration-validation`

## Violated Invariant

- Invariant: The deployment/genesis configuration pipeline should reject obviously invalid required parameters, especially non-zero privileged addresses and unsupported DA configuration combinations, before artifacts are generated.

## Trust Boundary

- Boundary: operator configuration -> deployment/genesis artifacts

## Attack Surface

- Entrypoint type: configuration-loader or deployment pipeline
- Sensitive sink: generation or activation of privileged protocol configuration

## Impact Pattern

- Primary impact: misconfiguration-risk
- Secondary impact: configuration-safety

## Short Reusable Lesson

- The deployment/genesis configuration pipeline should reject obviously invalid required parameters, especially non-zero privileged addresses and unsupported DA configuration combinations, before artifacts are generated. Similar bugs appear when configuration-loader or deployment pipeline code treats partially checked input as authoritative and lets it reach generation or activation of privileged protocol configuration. The reusable fix is to enforce configuration-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
