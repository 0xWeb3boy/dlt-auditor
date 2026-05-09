# Root-Cause Card

## Metadata

- ID: `solana-2019-12-20-solana-cryptography-3c361eb759`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `snapshot-integrity-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `snapshot-integrity-binding`

## Violated Invariant

- Protocol input must satisfy snapshot integrity binding before it can reach canonical bank state, account storage, snapshot acceptance, or ledger root.

## Trust Boundary

- Boundary: persisted or downloaded ledger/account state to trusted runtime reconstruction

## Attack Surface

- Entrypoint type: snapshot load, blockstore replay, accounts hash verification, or storage maintenance
- Sensitive sink: canonical bank state, account storage, snapshot acceptance, or ledger root

## Root Cause

The snapshot bank-hash verifier trusted stored per-account hash values as inputs to aggregate verification without first validating those values against the underlying account records.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Medium

## Short Reusable Lesson

The patch strengthens Solana snapshot/account verification by adding a per-account hash check in `runtime/src/accounts_db.rs::verify_bank_hash`. Before aggregation, the verifier now recomputes each non-sysvar account hash and returns `MismatchedAccountHash` if it differs from the stored `account.hash`. The `sdk/src/hash.rs` changes from literal `32` to `HASH_BYTES` are supporting cleanup and are not independent vulnerability evidence.
