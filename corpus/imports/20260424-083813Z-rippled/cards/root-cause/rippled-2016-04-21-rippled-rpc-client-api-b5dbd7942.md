# Root-Cause Card

## Metadata

- ID: `rippled-2016-04-21-rippled-rpc-client-api-b5dbd7942`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `failed-handshake-resource-accounting`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `accounting-integrity`

## Violated Invariant

- Invariant: Ledger accounting updates must preserve balance, reserve, fee, and yield invariants across every accepted transaction shape and lifecycle transition.

## Trust Boundary

- Boundary: remote client or configured service endpoint -> local RPC/client trust boundary

## Attack Surface

- Entrypoint type: rpc-or-client-handler
- Sensitive sink: node configuration, downloaded trust material, or externally visible service behavior

## Impact Pattern

- Primary impact: resource-exhaustion, denial-of-service
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The patch fixes overlay handoff rejection paths for malformed or unverifiable HELLO messages.
