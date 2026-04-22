# Root-Cause Card

## Metadata

- ID: `base-2026-04-15-base-consensus-388f5227e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validation-coverage-gap`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `coverage-completeness`

## Violated Invariant

- Invariant: Within the configured lookback window, the challenger should re-evaluate in-progress games when on-chain proof state changes, and it should not silently skip the observed dual-proof TEE+ZK no-challenge state.

## Trust Boundary

- Boundary: `on-chain dispute or engine state->off-chain consensus actor`

## Attack Surface

- Entrypoint type: `challenge-orchestration`
- Sensitive sink: `challenge outcome selection or dispute progression state`

## Impact Pattern

- Primary impact: `missed-validation`
- Secondary impact: `integrity-risk`

## Short Reusable Lesson

- Within the configured lookback window, the challenger should re-evaluate in-progress games when on-chain proof state changes, and it should not silently skip the observed dual-proof TEE+ZK no-challenge state. The scanner treated candidate discovery as mostly one-time state keyed by a scan watermark even though game state can change after first observation, and it encoded a classifier rule that treated a dual-proof no-challenge state as ignorable. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
