# Root-Cause Card

## Metadata

- ID: `sei-chain-2023-02-17-sei-chain-consensus-b5f113295`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-determinism-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `deterministic-state-transition-order`

## Violated Invariant

- Invariant: Consensus state transitions must not depend on language-level map iteration order or node-local ordering artifacts.

## Trust Boundary

- Boundary: validator-local in-memory collection -> consensus state transition

## Attack Surface

- Entrypoint type: beginblock-or-endblock-consensus-hook
- Sensitive sink: updating oracle, staking, or app-hash-relevant state

## Impact Pattern

- Primary impact: consensus-nondeterminism-risk
- Secondary impact: protocol-state-integrity

## Short Reusable Lesson

- Collect unordered map keys, sort them, and process values by sorted key in consensus-path code. Stage iterator values before performing additional store lookups or state-processing work. Oracle MidBlocker runs in a consensus-sensitive path. Go map iteration order is not a suitable source of protocol ordering. Deterministic ordering reduces the risk of node-to-node execution differences.
