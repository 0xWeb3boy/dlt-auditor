# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-m08-rebasing-token-escrow-drift`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `rebasing-token-escrow-supply-drift`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `rebasing-token backing reconciliation`

## Violated Invariant

- Invariant: A bank coin representation of escrowed ERC20 value must either exclude rebasing tokens or track changes in escrowed balance outside transfers.

## Trust Boundary

- Boundary: external ERC20 monetary policy->bank coin representation

## Attack Surface

- Entrypoint type: ERC20-to-bank and bank-to-ERC20 conversion
- Sensitive sink: escrowed ERC20 balance used to redeem fixed bank coin supply

## Impact Pattern

- Primary impact: escrow/backing drift for rebasing tokens
- Secondary impact: redemption failure or stranded excess escrow

## Short Reusable Lesson

- Conversion logic assumed escrowed ERC20 balance remains aligned with minted bank coin supply between conversion events, which rebasing tokens violate without transfer callbacks.
