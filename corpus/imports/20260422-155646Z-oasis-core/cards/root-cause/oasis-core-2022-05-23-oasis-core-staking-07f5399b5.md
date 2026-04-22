# Root-Cause Card

## Metadata

- ID: `oasis-core-2022-05-23-oasis-core-staking-07f5399b5`
- Bug family: `staking_registry_and_accountability`
- Bug class: `reserved-address-invariant-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `reserved-address-enforcement`

## Violated Invariant

- Invariant: 'staking.BurnAddress' must be treated as a burn sink, not as a normal transfer recipient, and ledger/genesis validation must reject non-zero balance or nonce for that address.

## Trust Boundary

- Boundary: `validator->consensus`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `reserved-address ledger state`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- 'staking.BurnAddress' must be treated as a burn sink, not as a normal transfer recipient, and ledger/genesis validation must reject non-zero balance or nonce for that address. In this pattern, 'staking.BurnAddress' was not handled consistently as a dedicated burn sink. The transfer path could treat it like a normal destination, and sanity checking did not enforce that the burn address remain unused in ledger/genesis state. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
