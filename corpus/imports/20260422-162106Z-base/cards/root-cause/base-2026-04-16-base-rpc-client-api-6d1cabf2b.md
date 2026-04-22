# Root-Cause Card

## Metadata

- ID: `base-2026-04-16-base-rpc-client-api-6d1cabf2b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-fraud-challenge-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: When handling a `FraudulentZkChallenge`, the challenger should judge the dispute using the single intermediate root identified by the on-chain challenged index, not by scanning unrelated intermediate roots and reacting to the first invalid one.

## Trust Boundary

- Boundary: `external chain or RPC data->node service`

## Attack Surface

- Entrypoint type: `challenge-orchestration`
- Sensitive sink: `challenge outcome selection or dispute progression state`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- When handling a `FraudulentZkChallenge`, the challenger should judge the dispute using the single intermediate root identified by the on-chain challenged index, not by scanning unrelated intermediate roots and reacting to the first invalid one. The challenger used validation scope that was broader than the decision boundary for this path. It considered all intermediate roots and derived the outcome from the first invalid one encountered, even though the dispute state identifies one specific challenged intermediate root index. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
