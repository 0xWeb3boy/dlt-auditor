# Root-Cause Card

## Metadata

- ID: `moonbeam-2025-04-28-moonbeam-transaction-processing-0e600693f7`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `target-based-proxy-call-filtering`

## Violated Invariant

- Invariant: A proxy authorization grants only the target classes permitted by the proxy type; broad proxy types must still apply explicit target filtering at the EVM boundary.

## Trust Boundary

- Boundary: An authorized proxy caller crosses into EVM subcall execution against precompiles, contracts, or externally owned accounts.

## Attack Surface

- Entrypoint type: evm-proxy-precompile-subcall
- Sensitive sink: proxied EVM call target selection

## Impact Pattern

- Primary impact: unauthorized-action
- Secondary impact: access-control, precompile-policy-bypass

## Short Reusable Lesson

- Runtime proxy filtering had an unconditional allow branch and a misclassified target branch. The fix classifies targets by code/precompile status and only allows intended target classes. Replace unconditional proxy allow logic with explicit target classification and whitelist-style policy for precompiles, no-code accounts, and contracts.
