# Root-Cause Card

## Metadata

- ID: `optimism-2024-01-29-optimism-transaction-processing-78e3cbb884`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: Post-Ecotone handling should use the intended EIP-4788 deployment bytes and should apply the beacon-root state update whenever a header carries ParentBeaconRoot, so derived execution state matches the protocol rules.

## Trust Boundary

- Boundary: operator configuration -> deployment/genesis artifacts

## Attack Surface

- Entrypoint type: configuration-loader or deployment pipeline
- Sensitive sink: generation or activation of privileged protocol configuration

## Impact Pattern

- Primary impact: consensus-divergence-risk
- Secondary impact: state-transition-risk

## Short Reusable Lesson

- Post-Ecotone handling should use the intended EIP-4788 deployment bytes and should apply the beacon-root state update whenever a header carries ParentBeaconRoot, so derived execution state matches the protocol rules. Similar bugs appear when configuration-loader or deployment pipeline code treats partially checked input as authoritative and lets it reach generation or activation of privileged protocol configuration. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
