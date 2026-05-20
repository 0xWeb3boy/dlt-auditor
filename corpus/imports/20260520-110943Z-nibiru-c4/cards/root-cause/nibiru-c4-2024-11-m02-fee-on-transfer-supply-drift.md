# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-m02-fee-on-transfer-supply-drift`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `fee-on-transfer-supply-drift`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `supply-backing invariant enforcement`

## Violated Invariant

- Invariant: Bank coin supply minted for escrowed ERC20s must be fully burned for the user-submitted bank amount when converting back, even if the outbound ERC20 transfer takes a fee.

## Trust Boundary

- Boundary: external fee-on-transfer ERC20->bank coin representation

## Attack Surface

- Entrypoint type: bank-coin-to-EVM conversion transaction
- Sensitive sink: bank coin burn amount during ERC20-born FunToken conversion

## Impact Pattern

- Primary impact: unbacked bank coin supply drift
- Secondary impact: incorrect total supply accounting

## Short Reusable Lesson

- convertCoinToEvmBornERC20 transferred the full requested ERC20 amount but burned only actualSentAmount after transfer fees.
