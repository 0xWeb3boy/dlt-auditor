# Root-Cause Card

## Metadata

- ID: `base-2025-10-14-base-rpc-client-api-f694185fe`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-state-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Invariant: If cached L1 checkpoint data is reused for an existing aggregation request, it should match the contract's canonical historic block-hash mapping for that block number before the proposer relies on it.

## Trust Boundary

- Boundary: `external chain or RPC data->node service`

## Attack Surface

- Entrypoint type: `external-state-ingestion`
- Sensitive sink: `reuse of cached checkpoint or execution data that drives proposer or validator actions`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- If cached L1 checkpoint data is reused for an existing aggregation request, it should match the contract's canonical historic block-hash mapping for that block number before the proposer relies on it. The retry/reuse path trusted locally cached checkpoint data without first confirming it against the contract's authoritative historic block-hash mapping. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
