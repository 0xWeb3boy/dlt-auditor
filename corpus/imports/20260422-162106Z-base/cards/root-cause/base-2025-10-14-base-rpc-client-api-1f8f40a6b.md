# Root-Cause Card

## Metadata

- ID: `base-2025-10-14-base-rpc-client-api-1f8f40a6b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Invariant: A cached checkpoint from an existing aggregation request should only be reused if it is still consistent with the contract's current historic block-hash mapping for that block number; matching request parameters alone are not sufficient.

## Trust Boundary

- Boundary: `external chain or RPC data->node service`

## Attack Surface

- Entrypoint type: `external-state-ingestion`
- Sensitive sink: `reuse of cached checkpoint or execution data that drives proposer or validator actions`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- A cached checkpoint from an existing aggregation request should only be reused if it is still consistent with the contract's current historic block-hash mapping for that block number; matching request parameters alone are not sufficient. The proposer flow appears to have treated cached checkpoint data from a prior matching request as reusable authority without first revalidating it against the contract's current canonical historic block-hash mapping. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
