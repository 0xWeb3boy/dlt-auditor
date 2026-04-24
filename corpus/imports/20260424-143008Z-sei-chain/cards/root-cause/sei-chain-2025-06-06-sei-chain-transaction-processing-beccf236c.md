# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-06-06-sei-chain-transaction-processing-beccf236c`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-message-validation`

## Violated Invariant

- Invariant: Alternate runtime entrypoints must execute through the same message validation and dispatch path as native transactions.

## Trust Boundary

- Boundary: EVM precompile caller -> Cosmos governance module state

## Attack Surface

- Entrypoint type: precompile-transaction-handler
- Sensitive sink: depositing, voting, or mutating governance state

## Impact Pattern

- Primary impact: governance-validation-divergence
- Secondary impact: protocol-state-integrity

## Short Reusable Lesson

- Align EVM precompile transaction execution with the canonical Cosmos SDK governance message path by constructing Msg objects, validating them, and using MsgServer dispatch instead of direct keeper mutation. Keeps EVM precompile behavior closer to native governance transaction behavior. Reduces risk of divergence between direct keeper calls and message-level validation.
