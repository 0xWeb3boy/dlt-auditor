# Root-Cause Card

## Metadata

- ID: `reth-2026-03-21-reth-transaction-processing-b78f74f52`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `validation-gate-enforcement`

## Violated Invariant

- Invariant: Core payload integrity checks should not be disabled by special-case block formats. A payload's declared block hash should match the reconstructed block hash, and executed state should still be checked against the header state root unless a specific field is known to be non-comparable.

## Trust Boundary

- Boundary: block or transaction input -> execution-layer validator

## Attack Surface

- Entrypoint type: transaction/block-validation-path
- Sensitive sink: transaction acceptance or consensus rule application

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: none proven

## Short Reusable Lesson

- Core payload integrity checks should not be disabled by special-case block formats. A payload's declared block hash should match the reconstructed block hash, and executed state should still be checked against the header state root unless a specific field is known to be non-comparable.
