# Root-Cause Card

## Metadata

- ID: `solana-2020-11-13-solana-transaction-processing-f6b65b033e`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `arithmetic-overflow-in-validation-counter`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `checked-arithmetic-bounds`

## Violated Invariant

- Protocol input must satisfy checked arithmetic bounds before it can reach canonical bank state, account storage, snapshot acceptance, or ledger root.

## Trust Boundary

- Boundary: persisted or downloaded ledger/account state to trusted runtime reconstruction

## Attack Surface

- Entrypoint type: snapshot load, blockstore replay, accounts hash verification, or storage maintenance
- Sensitive sink: canonical bank state, account storage, snapshot acceptance, or ledger root

## Root Cause

The verifier used overflow-sensitive arithmetic for a validation counter whose value determines whether a tick hash count is accepted or rejected.

## Impact Pattern

- Primary impact: validation-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch fixes overflow-sensitive arithmetic in `ledger/src/entry.rs` during tick hash count verification. The running `tick_hash_count` previously used direct `u64` addition and now uses `saturating_add`, so oversized cumulative counts cannot wrap before the exact equality check against `hashes_per_tick`.
