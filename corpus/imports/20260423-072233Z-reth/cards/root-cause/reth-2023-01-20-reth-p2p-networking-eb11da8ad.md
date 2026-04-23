# Root-Cause Card

## Metadata

- ID: `reth-2023-01-20-reth-p2p-networking-eb11da8ad`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-handshake-state-inconsistency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- This patch is supported as a protocol-correctness and hardening change in network handshake setup, not as a demonstrated vulnerability fix. The visible code centralizes derivation of `Status` and `ForkFilter` from `ChainSpec` and a resolved head so those handshake inputs cannot diverge through separate builder state or different defaults.
