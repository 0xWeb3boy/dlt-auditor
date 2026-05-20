# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ts-sdk-pending-utxo-awareness-33360`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `pending-utxo-reservation-missing`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `pending-spend-accounting`

## Violated Invariant

- Client-side coin selection must not reuse a UTXO already reserved by another pending transaction from the same account.

## Trust Boundary

- Boundary: `wallet-account-state->transaction-builder`
- Entrypoint type: `sdk-funding-helper`
- Sensitive sink: `transaction inputs selected for newly funded requests`

## Attack Surface

- Ask the SDK to fund multiple transactions in the same block interval.
- Submit a first transaction before the node's GraphQL state removes its input.

## Exploit Preconditions

- The fund helper queries spendable resources statelessly.
- The node still reports the UTXO until a block consumes it or txpool state is considered.

## Impact Pattern

- Primary impact: `transaction-liveness`
- Secondary impact: `mempool-consistency`
- Blast radius: `client-local`
- Severity guess: `medium`

## Short Reusable Lesson

- UTXO wallets need a pending-spend model; confirmed state alone is stale between submission and block inclusion.
