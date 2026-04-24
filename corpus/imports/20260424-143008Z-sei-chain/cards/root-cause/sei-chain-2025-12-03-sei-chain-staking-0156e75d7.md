# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-12-03-sei-chain-staking-0156e75d7`
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

- Do not place raw or stringified error messages into consensus-visible return data on failed precompile execution. Preserve failure signaling through the VM error path and leave return data nil for errored precompile calls. Protects consensus-hashed transaction result fields from nondeterministic error strings.
