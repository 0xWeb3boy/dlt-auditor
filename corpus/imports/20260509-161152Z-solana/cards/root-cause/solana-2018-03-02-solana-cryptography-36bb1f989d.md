# Root-Cause Card

## Metadata

- ID: `solana-2018-03-02-solana-cryptography-36bb1f989d`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `double-spend-stale-accounting`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `immediate-state-reservation`

## Violated Invariant

- Accepted spends must reserve or update spendable balance before any later spend is checked against the same account state.

## Trust Boundary

- Boundary: signed client spend event to local accountant balance state and historian logging

## Attack Surface

- Entrypoint type: signed deposit or transfer event accepted by the transaction-accounting path
- Sensitive sink: account balance mutation, spend acceptance, and signature reservation

## Root Cause

The accountant did not immediately reflect a previously accepted spend in local balance state, so a later spend could be checked before the earlier one had been processed. That stale-balance window allowed double-spend behavior in this transaction-accounting path.

## Impact Pattern

- Primary impact: double-spend, unauthorized-spend
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

Confirmed security fix for a double-spend window in the accountant/historian transaction path. The commit explicitly states that a client could spend funds before the accountant processed a previous spend, and the patch moves signed-event validation into the accountant path while updating balances immediately rather than depending only on later historian processing.
