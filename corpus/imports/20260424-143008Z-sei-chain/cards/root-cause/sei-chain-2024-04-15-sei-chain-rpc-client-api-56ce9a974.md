# Root-Cause Card

## Metadata

- ID: `sei-chain-2024-04-15-sei-chain-rpc-client-api-56ce9a974`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `identity-binding-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `address-association-check`

## Violated Invariant

- Invariant: Cross-address payload construction must require an explicit state-backed identity association before using either identity in a privileged call.

## Trust Boundary

- Boundary: wasm or RPC query parameter -> EVM/precompile call payload

## Attack Surface

- Entrypoint type: query-payload-builder
- Sensitive sink: ABI-packing token or precompile call data with participant addresses

## Impact Pattern

- Primary impact: identity-confusion
- Secondary impact: unauthorized-operation-prevention

## Short Reusable Lesson

- Replace default-derived address resolution with explicit state-backed lookup and fail closed when no association exists. Enforces explicit address association in the shown payload builders. Prevents silent use of default-derived EVM identities in these paths. May reduce identity-confusion risk around precompile-related call data.
