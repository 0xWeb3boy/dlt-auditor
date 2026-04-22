# Root-Cause Card

## Metadata

- ID: `base-2026-04-16-base-rpc-client-api-9cd40e7d7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-challenge-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: When handling a fraudulent ZK challenge, the challenger should decide based on the validity of the specific intermediate root that was challenged on-chain, not on unrelated earlier intermediate roots.

## Trust Boundary

- Boundary: `external chain or RPC data->node service`

## Attack Surface

- Entrypoint type: `challenge-orchestration`
- Sensitive sink: `challenge outcome selection or dispute progression state`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `protection-bypass`

## Short Reusable Lesson

- When handling a fraudulent ZK challenge, the challenger should decide based on the validity of the specific intermediate root that was challenged on-chain, not on unrelated earlier intermediate roots. The decision logic in the challenger used validation results for all intermediate roots rather than the single root referenced by the on-chain challenge. That incorrect scope allowed unrelated invalid roots to influence the nullification decision. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
