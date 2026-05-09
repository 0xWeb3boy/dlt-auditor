# Root-Cause Card

## Metadata

- ID: `solana-2019-02-22-solana-transaction-processing-66891d9d4e`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization-and-privilege-check`

## Violated Invariant

- Protocol input must satisfy authorization and privilege check before it can reach canonical bank state, account storage, snapshot acceptance, or ledger root.

## Trust Boundary

- Boundary: persisted or downloaded ledger/account state to trusted runtime reconstruction

## Attack Surface

- Entrypoint type: snapshot load, blockstore replay, accounts hash verification, or storage maintenance
- Sensitive sink: canonical bank state, account storage, snapshot acceptance, or ledger root

## Root Cause

The storage program design used a shared/global storage account as a userdata target instead of keeping state scoped to the signed account supplied to the instruction. The provided evidence indicates the old path depended on `keyed_accounts[1]` matching `storage_program::system_id()`, while an owner check was only present as commented TODO text. The complete mutation site is not shown, so the root cause should not be stated more strongly than this.

## Impact Pattern

- Primary impact: unauthorized-state-modification
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch likely fixes an access-control flaw in Solana's native storage program by removing the separate global storage account userdata path. The strongest grounded evidence is the entrypoint change from two accounts to one signed account, removal of the `keyed_accounts[1]`/`storage_program::system_id()` path, and deletion of bank code that read storage state from that global account. The commit body also states that other accounts should not be able...
