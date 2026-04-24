# Root-Cause Card

## Metadata

- ID: `sei-chain-2024-04-15-sei-chain-rpc-client-api-a2aa14179`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-address-association-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `address-association-check`

## Violated Invariant

- Invariant: Cross-runtime address parameters must be mapped through explicit association state before they are used in EVM or precompile payloads.

## Trust Boundary

- Boundary: wasm query caller -> EVM address/precompile payload builder

## Attack Surface

- Entrypoint type: query-payload-builder
- Sensitive sink: constructing ABI call data for token or precompile operations

## Impact Pattern

- Primary impact: identity-binding
- Secondary impact: access-control

## Short Reusable Lesson

- Replace default-or-derived address conversion with explicit lookup and negative-path rejection before constructing EVM call payloads or query data. Prevents these helpers from silently converting unassociated Bech32 addresses into EVM address parameters. Strengthens Cosmos-to-EVM identity binding for selected wasm EVM ERC20/ERC721 helper calls.
