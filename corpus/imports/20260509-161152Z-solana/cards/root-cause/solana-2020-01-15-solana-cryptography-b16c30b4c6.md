# Root-Cause Card

## Metadata

- ID: `solana-2020-01-15-solana-cryptography-b16c30b4c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-hash-alignment-bug`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-root-consistency`

## Violated Invariant

- Protocol input must satisfy state root consistency before it can reach canonical bank state, account storage, snapshot acceptance, or ledger root.

## Trust Boundary

- Boundary: persisted or downloaded ledger/account state to trusted runtime reconstruction

## Attack Surface

- Entrypoint type: snapshot load, blockstore replay, accounts hash verification, or storage maintenance
- Sensitive sink: canonical bank state, account storage, snapshot acceptance, or ledger root

## Root Cause

`store_accounts` tracked partial append progress in `infos.len()` but applied that offset only to the account metadata slice, not to the parallel hash slice. Since `append_accounts` consumes account metadata and hashes positionally, inconsistent slicing could persist mismatched account/hash pairs.

## Impact Pattern

- Primary impact: liveness, state-integrity
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch fixes an offset mismatch in `AccountsDB::store_accounts`. Before the change, remaining account metadata was sliced with `infos.len()` after partial append progress, but the hashes argument still started at the beginning of the original hash slice. After the change, hashes are sliced with the same offset, preserving account-to-hash alignment. The commit message and added bank-hash test support a consensus/liveness relevance, but the provided ev...
