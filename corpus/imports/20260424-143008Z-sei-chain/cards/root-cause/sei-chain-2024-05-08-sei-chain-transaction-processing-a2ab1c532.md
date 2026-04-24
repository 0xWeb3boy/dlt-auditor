# Root-Cause Card

## Metadata

- ID: `sei-chain-2024-05-08-sei-chain-transaction-processing-a2ab1c532`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `monetary-accounting-invariant`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `ledger-accounting-consistency`

## Violated Invariant

- Invariant: All execution paths that create, burn, defer, or repair balances must preserve the same ledger accounting invariant at block finalization.

## Trust Boundary

- Boundary: transaction execution accounting delta -> bank supply and end-block state

## Attack Surface

- Entrypoint type: ante-finalization-or-endblock-accounting
- Sensitive sink: updating balances, surplus, or total supply

## Impact Pattern

- Primary impact: supply-integrity
- Secondary impact: accounting-integrity

## Short Reusable Lesson

- Move accounting deltas into keeper-managed state, aggregate related surplus values at EndBlock, net positive and negative values before adding balances, and repair historical total supply drift with a targeted migration. Protects the chain's monetary accounting invariant. Prevents surplus values from being added before proper netting.
