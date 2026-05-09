# Root-Cause Card

## Metadata

- ID: `nibiru-2026-04-27-nibiru-transaction-processing-224de766`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization for asset mapping creation`

## Violated Invariant

- Invariant: Creation of mainnet asset mappings that bind external token contracts to native denominations must be restricted to governance, authority, or explicitly permissioned accounts.

## Trust Boundary

- Boundary: Externally submitted mapping-creation transaction crosses into privileged registry state for bridge assets.

## Attack Surface

- Entrypoint type: CreateFunToken message handler
- Sensitive sink: FunToken mapping registry and fee/registration flow

## Impact Pattern

- Primary impact: unauthorized asset mapping creation
- Secondary impact: downstream bridge/precompile misuse

## Short Reusable Lesson

- A public asset-mapping creation path gained a mainnet-only authority/sudo gate before registration can proceed.
