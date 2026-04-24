# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-12-03-sei-chain-staking-b5f8936e8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-nondeterminism-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `deterministic-consensus-error-data`

## Violated Invariant

- Invariant: Consensus-visible execution result data must not contain node-local diagnostics or nondeterministic error strings.

## Trust Boundary

- Boundary: precompile failure or VM error -> ABCI result data/results hash

## Attack Surface

- Entrypoint type: precompile-execution-handler
- Sensitive sink: returning execution data included in consensus result hashing

## Impact Pattern

- Primary impact: consensus-divergence
- Secondary impact: chain-halt

## Short Reusable Lesson

- Keep nondeterministic diagnostics out of consensus-relevant serialized fields. Signal precompile failure through deterministic error handling while returning nil bytes instead of stringified error text on failed execution. Consensus result hashes must be identical across nodes. Error strings can vary by environment, wrapping, or stack details.
