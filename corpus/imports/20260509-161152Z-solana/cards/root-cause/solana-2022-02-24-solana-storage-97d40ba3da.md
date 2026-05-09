# Root-Cause Card

## Metadata

- ID: `solana-2022-02-24-solana-storage-97d40ba3da`
- Bug family: `authz_and_role_gates`
- Bug class: `rent-state-validation-bypass`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-shape-validation`

## Violated Invariant

- Protocol input must satisfy input shape validation before it can reach canonical bank state, account storage, snapshot acceptance, or ledger root.

## Trust Boundary

- Boundary: persisted or downloaded ledger/account state to trusted runtime reconstruction

## Attack Surface

- Entrypoint type: snapshot load, blockstore replay, accounts hash verification, or storage maintenance
- Sensitive sink: canonical bank state, account storage, snapshot acceptance, or ledger root

## Root Cause

The rent-state transition check treated `RentPaying` primarily as a category and did not enforce the `RentPaying(data_size)` component for accounts that were already rent paying. That left a validation gap for legacy rent-paying accounts whose data length changed during transaction execution.

## Impact Pattern

- Primary impact: economic-integrity, state-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch likely fixes a runtime rent-state validation bypass. The central supported change is in `runtime/src/account_rent_state.rs`, where `RentState::transition_allowed_from` now carries `do_support_realloc` and compares pre/post data sizes for `RentPaying(data_size)` accounts. This supports the commit subject that resized accounts must be rent exempt. The evidence does not support the heuristic claims about panics, malformed decoding, cryptographic...
