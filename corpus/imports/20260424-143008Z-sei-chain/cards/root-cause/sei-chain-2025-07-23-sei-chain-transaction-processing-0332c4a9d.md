# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-07-23-sei-chain-transaction-processing-0332c4a9d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `entrypoint-scope-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `entrypoint-scope-and-message-type-check`

## Violated Invariant

- Invariant: Generic and scoped claim/transfer entrypoints must reject messages whose concrete type or caller runtime is outside that entrypoint scope.

## Trust Boundary

- Boundary: EVM/CosmWasm caller -> precompile value-transfer entrypoint

## Attack Surface

- Entrypoint type: precompile-claim-handler
- Sensitive sink: transferring all balances or scoped assets

## Impact Pattern

- Primary impact: authorization-scope
- Secondary impact: cross-runtime-access-control

## Short Reusable Lesson

- Enforce message type and call-boundary checks at precompile entrypoints before value transfer, and ensure serialized asset fields needed for scoped execution are decoded. Specific-asset claim messages should not be processed by a generic all-balances claim path. The fix aligns the validated message type with the selected precompile entrypoint before transfer.
