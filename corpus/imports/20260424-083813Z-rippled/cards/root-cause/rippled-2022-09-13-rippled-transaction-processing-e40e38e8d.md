# Root-Cause Card

## Metadata

- ID: `rippled-2022-09-13-rippled-transaction-processing-e40e38e8d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unauthorized-resource-consumption`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Ledger accounting updates must preserve balance, reserve, fee, and yield invariants across every accepted transaction shape and lifecycle transition.

## Trust Boundary

- Boundary: externally submitted action -> account, delegate, or role authorization gate

## Attack Surface

- Entrypoint type: authorization-check-path
- Sensitive sink: privileged account action, delegated permission, or role-scoped state change

## Impact Pattern

- Primary impact: resource-exhaustion, economic-denial-of-service
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The patch removes the NFTokenMint tfTrustLine capability through the fixRemoveNFTokenAutoTrustLine amendment.
