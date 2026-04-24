# Root-Cause Card

## Metadata

- ID: `geth-arb-2017-08-25-go-ethereum-storage-08f27428b4`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `contract-address-collision-prevention`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `account-creation-collision-check`

## Violated Invariant

- Invariant: Contract creation must fail when the destination account already has nonce or code state that makes the address occupied under the active fork rules.

## Trust Boundary

- Boundary: transaction CREATE operation -> account/state allocation

## Attack Surface

- Entrypoint type: EVM CREATE/contract deployment path
- Sensitive sink: new contract account creation and code installation

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: contract-deployment-integrity
- Severity guide: medium

## Short Reusable Lesson

- The CREATE path needed an explicit occupied-account check so deployment could not overwrite or collide with existing nonce/code state under the fork rule. Compute the destination address before creation, check nonce and code hash, and return a collision error before code installation.
