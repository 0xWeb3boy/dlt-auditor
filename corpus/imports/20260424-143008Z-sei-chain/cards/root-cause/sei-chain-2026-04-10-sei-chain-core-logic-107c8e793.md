# Root-Cause Card

## Metadata

- ID: `sei-chain-2026-04-10-sei-chain-core-logic-107c8e793`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-discriminator-consistency`

## Violated Invariant

- Invariant: Protocol stream discriminator fields must be explicit on creation and consistent with stored stream state on reuse.

## Trust Boundary

- Boundary: remote p2p mux header -> local stream state and resource limits

## Attack Surface

- Entrypoint type: p2p-mux-header-handler
- Sensitive sink: creating or accepting multiplexed inbound streams

## Impact Pattern

- Primary impact: resource-limit-enforcement
- Secondary impact: protocol-state-integrity

## Short Reusable Lesson

- Tighten protocol boundary validation by requiring explicit discriminator fields on creation and checking discriminator consistency against stored stream state. Prevents silent defaulting of missing stream kind to kind 0. Makes stream-kind consistency explicit in the mux state machine. Supports cleaner inbound accept-limit enforcement by requiring explicit kind data.
