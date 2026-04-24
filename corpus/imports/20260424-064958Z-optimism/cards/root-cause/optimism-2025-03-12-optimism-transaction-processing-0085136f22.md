# Root-Cause Card

## Metadata

- ID: `optimism-2025-03-12-optimism-transaction-processing-0085136f22`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-integrity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `configuration-validation`

## Violated Invariant

- Invariant: A deployment should only reuse the predeployed OPCM and shared global SuperchainConfig when the intent is explicitly on the standard path and still matches the standard superchain authority set; customized intents should not silently inherit shared governance settings.

## Trust Boundary

- Boundary: operator configuration -> deployment/genesis artifacts

## Attack Surface

- Entrypoint type: configuration-loader or deployment pipeline
- Sensitive sink: generation or activation of privileged protocol configuration

## Impact Pattern

- Primary impact: misconfiguration
- Secondary impact: governance-config-exposure

## Short Reusable Lesson

- A deployment should only reuse the predeployed OPCM and shared global SuperchainConfig when the intent is explicitly on the standard path and still matches the standard superchain authority set; customized intents should not silently inherit shared governance settings. Similar bugs appear when configuration-loader or deployment pipeline code treats partially checked input as authoritative and lets it reach generation or activation of privileged protocol configuration. The reusable fix is to enforce configuration-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
