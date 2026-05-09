---
case_id: case_20200115_b16c30b4c6
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2020-01-15
source_refs:
  - git:b16c30b4c66a42d55b989a929bb3d08c44159ab0
  - "runtime/src/accounts_db.rs:2380"
  - "runtime/src/accounts_db.rs:959"
bug_class: state-hash-alignment-bug
impact_type:
  - liveness
  - state-integrity
tags:
  - runtime
  - accounts-db
  - bank-hash
  - state-integrity
  - liveness
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes an offset mismatch in `AccountsDB::store_accounts`. Before the change, remaining account metadata was sliced with `infos.len()` after partial append progress, but the hashes argument still started at the beginning of the original hash slice. After the change, hashes are sliced with the same offset, preserving account-to-hash alignment. The commit message and added bank-hash test support a consensus/liveness relevance, but the provided evidence does not establish attacker control or a specific remote exploit path.

## Observed Patch Facts

1. In `runtime/src/accounts_db.rs`, the patch adds `#[test]`.

2. In `runtime/src/accounts_db.rs`, the patch replaces `.append_accounts(&with_meta[infos.len()..], &hashes);` with `.append_accounts(&with_meta[infos.len()..], &hashes[infos.len()..]);`.

## Project Context

The changed code sits primarily in `runtime/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `runtime/src/accounts.rs`, `runtime/src/accounts_index.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/accounts.rs`, `runtime/src/accounts_index.rs`. The strongest project-level identifiers around this patch are `solana_sdk::signature`, `AccountsDB::new`, `Vec::new`, and `AccountStorageStatus::Full`.

## Before/After Behavior

Before the patch, a resumed or chunked append used `&with_meta[infos.len()..]` for accounts but passed unshifted `&hashes`, allowing later accounts to be paired with earlier hashes when `infos.len()` was nonzero. After the patch, the call uses `&hashes[infos.len()..]`, so account metadata and hashes advance together across partial storage progress.

# Root Cause

`store_accounts` tracked partial append progress in `infos.len()` but applied that offset only to the account metadata slice, not to the parallel hash slice. Since `append_accounts` consumes account metadata and hashes positionally, inconsistent slicing could persist mismatched account/hash pairs.

## Walkthrough

1. `store_accounts` receives accounts and a corresponding `hashes` slice.

2. It builds `with_meta` and appends accounts while `infos.len() < with_meta.len()`.

3. The append loop may make partial progress, leaving `infos.len()` nonzero before the next append.

4. Before the fix, the next append used shifted account metadata but unshifted hashes.

5. That could associate remaining accounts with hashes from the start of the original slice.

6. The fix changes the hash argument to `&hashes[infos.len()..]`.

7. A regression test for bad bank hash behavior was added near existing account hash mismatch coverage.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/accounts_db.rs | 932 | AccountsDB::store_accounts builds account metadata and stores accounts with corresponding hashes across possibly multiple storage appends. |
| runtime/src/accounts_db.rs | 959 | Fix shifts the hashes slice by `infos.len()` so remaining accounts and hashes stay aligned after partial progress. |
| runtime/src/accounts_db.rs | 2359 | Existing bank hash verification test context checks detection of mismatched account hashes. |
| runtime/src/accounts_db.rs | 2380 | New regression test exercises bad bank hash/account hash mismatch behavior. |

## Code Snippets

## Snippet 1

Context: `runtime/src/accounts_db.rs:2380` (changes signature or replay validation logic)

Before
```rust
);
    }
}
```
After
```rust
);
    }

    #[test]
    fn test_bad_bank_hash() {
        use solana_sdk::signature::{Keypair, KeypairUtil};
        let db = AccountsDB::new(Vec::new());
```

## Snippet 2

Context: `runtime/src/accounts_db.rs:959` (changes a sensitive control or state-update path)

Before
```rust
let rvs = storage
                .accounts
                .append_accounts(&with_meta[infos.len()..], &hashes);
            if rvs.is_empty() {
                storage.set_status(AccountStorageStatus::Full);
```
After
```rust
let rvs = storage
                .accounts
                .append_accounts(&with_meta[infos.len()..], &hashes[infos.len()..]);
            if rvs.is_empty() {
                storage.set_status(AccountStorageStatus::Full);
```

# Fix Pattern

When passing parallel slices through retry, chunking, or partial-progress logic, apply the same progress offset to every positionally coupled input.

## How It Was Fixed

The implementation changed `append_accounts(&with_meta[infos.len()..], &hashes)` to `append_accounts(&with_meta[infos.len()..], &hashes[infos.len()..])` in `runtime/src/accounts_db.rs`. A new `test_bad_bank_hash` was added in the same file.

# Why It Matters

1. Preserves account-to-hash alignment in runtime storage.

2. Avoids incorrect persisted account hashes after partial append progress.

3. Protects bank hash verification from internally inconsistent stored state.

4. Relevant to consensus state integrity and liveness, based on the commit message and test context.

# Evidence Notes

The strongest evidence is the one-line implementation fix in `runtime/src/accounts_db.rs` and the surrounding `store_accounts` loop showing `infos.len()` as the partial-progress offset. The new test and existing nearby `MismatchedAccountHash` test support the bank-hash mismatch interpretation. Claims about malformed transaction decoding, signature validation, confidentiality impact, fund theft, authorization bypass, or cryptographic primitive failure are unsupported by the provided evidence. External exploitability is also not established. Protocol security invariant: Accounts written into AccountsDB must remain positionally aligned with the hashes used for bank/account state verification. If storage append resumes from a nonzero offset after partial progress, both the account metadata slice and the hash slice must advance by the same offset. Verification notes: The patch does not show malformed transaction decoding or signature validation behavior. The patch does not prove remote exploitability or an attacker-controlled path to force the storage boundary condition. The patch does not show fund theft, authorization bypass, or account ownership violation. The security relevance is consensus/state-integrity and liveness, not confidentiality or cryptographic primitive failure. Grounded in the changed `append_accounts` arguments. Grounded in the surrounding loop over partial append progress. Supported by commit text mentioning cluster collapse and bank hash mismatch. Downgraded from high confidence because the provided evidence does not show an attacker-controlled trigger or exploit path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `state-hash-alignment-bug`
Final impact type: `liveness, state-integrity`
Final tags: `runtime, accounts-db, bank-hash, state-integrity, liveness`

The supplied patch evidence supports a consensus/runtime state-integrity hardening case: a partial append path advanced account metadata without advancing the parallel hash slice, and the fix realigns those inputs. The commit message references cluster collapse and the added test targets bank hash mismatch, which makes liveness/state-integrity relevance plausible. However, the evidence does not prove attacker control or a concrete exploit path, so this should not be kept as a confident security-fix case.

## Security Evidence

1. Fix changes append_accounts from using unshifted hashes to hashes sliced by infos.len(), matching the shifted account metadata slice.
2. The affected code is AccountsDB storage for account data and account hashes, which feed bank/account hash verification.
3. Regression evidence references bad bank hash and mismatched account hash behavior.
4. Commit subject states cluster collapse due to improper shifted read.

## Missing Evidence

1. No evidence shows an external attacker can force the partial append condition.
2. No exploit path from transactions, RPC, replay, or malformed input is demonstrated.
3. No evidence shows fund theft, authorization bypass, confidentiality impact, or signature verification failure.
4. The patch alone does not prove a concrete consensus safety violation beyond plausible liveness/state-integrity risk.

## Claim Boundaries

1. Classify as security-hardening, not a proven security-fix.
2. Security relevance is limited to runtime state integrity and possible cluster liveness impact.
3. Do not describe this as a cryptographic primitive bug or signature validation flaw.
4. Do not claim remote exploitability or attacker-controlled triggering from the provided evidence.
