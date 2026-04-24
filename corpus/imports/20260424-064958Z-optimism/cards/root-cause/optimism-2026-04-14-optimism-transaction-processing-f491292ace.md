# Root-Cause Card

## Metadata

- ID: `optimism-2026-04-14-optimism-transaction-processing-f491292ace`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validation-configuration-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `configuration-validation`

## Violated Invariant

- Invariant: If a message expiry window is configured in the dependency set, supernode interop validation should use that same window rather than an unrelated hardcoded default.

## Trust Boundary

- Boundary: operator configuration -> deployment/genesis artifacts

## Attack Surface

- Entrypoint type: configuration-loader or deployment pipeline
- Sensitive sink: generation or activation of privileged protocol configuration

## Impact Pattern

- Primary impact: validation-bypass-risk
- Secondary impact: security-hardening-or-correctness

## Short Reusable Lesson

- If a message expiry window is configured in the dependency set, supernode interop validation should use that same window rather than an unrelated hardcoded default. Similar bugs appear when configuration-loader or deployment pipeline code treats partially checked input as authoritative and lets it reach generation or activation of privileged protocol configuration. The reusable fix is to enforce configuration-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
