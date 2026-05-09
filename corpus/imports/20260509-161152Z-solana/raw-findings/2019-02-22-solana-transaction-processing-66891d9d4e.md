---
case_id: case_20190222_66891d9d4e
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: access-control
confidence: medium
source_quality: high
date: 2019-02-22
source_refs:
  - git:66891d9d4eec243585ce222d55f2846b97f06474
  - "runtime/src/bank.rs:231"
  - "programs/native/storage/src/lib.rs:46"
  - "programs/native/storage/src/lib.rs:34"
  - "runtime/src/bank.rs:1199"
impact_type:
  - unauthorized-state-modification
tags:
  - infrastructure
  - storage-program
  - access-control
  - userdata
  - account-state-isolation
  - global-account-removal
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes an access-control flaw in Solana's native storage program by removing the separate global storage account userdata path. The strongest grounded evidence is the entrypoint change from two accounts to one signed account, removal of the `keyed_accounts[1]`/`storage_program::system_id()` path, and deletion of bank code that read storage state from that global account. The commit body also states that other accounts should not be able to modify system-account userdata. The evidence does not show the complete write path or a concrete exploit, so the verdict is likely rather than confirmed.

## Observed Patch Facts

1. In `runtime/src/bank.rs`, the patch replaces `pub fn get_storage_entry_height(&self) -> u64 {` with `/// Forget all signatures. Useful for benchmarking.`.

2. In `programs/native/storage/src/lib.rs`, the patch replaces `// Following https://github.com/solana-labs/solana/pull/2773,` with `if let Ok(syscall) = bincode::deserialize(data) {`.

3. In `programs/native/storage/src/lib.rs`, the patch replaces `if keyed_accounts.len() != 2 {` with `if keyed_accounts.len() != 1 {`.

4. In `runtime/src/bank.rs`, the patch removes `let storage_system = Pubkey::new(&[`.

## Project Context

The changed code sits primarily in `runtime/src`, `programs/native/storage/src`, `programs/native/storage`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/src/runtime.rs`, `runtime/src/accounts.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/runtime.rs`, `runtime/src/accounts.rs`. The strongest project-level identifiers around this patch are `state`, `keyed_accounts`, `userdata`, and `storage_program::system_id`. Nearby tests or test-like files include `programs/native/storage/tests/storage.rs`.

## Before/After Behavior

Before the patch, the storage entrypoint accepted two accounts, required `keyed_accounts[0]` to be signed, and used `keyed_accounts[1]` as the storage userdata account after checking that its key matched `system_id()`. `Bank::get_storage_entry_height()` also read `StorageProgramState` from `storage_program::system_id()` account userdata. After the patch, the storage entrypoint expects one account, keeps the signer requirement on `keyed_accounts[0]`, and deserializes storage state from `keyed_accounts[0].account.userdata`; the bank helper and separate storage-system test id were removed.

# Root Cause

The storage program design used a shared/global storage account as a userdata target instead of keeping state scoped to the signed account supplied to the instruction. The provided evidence indicates the old path depended on `keyed_accounts[1]` matching `storage_program::system_id()`, while an owner check was only present as commented TODO text. The complete mutation site is not shown, so the root cause should not be stated more strongly than this.

## Walkthrough

1. The old storage entrypoint rejected calls unless two accounts were supplied.

2. The first account was required to sign, but the removed global-storage path involved `keyed_accounts[1]`.

3. Removed code checked that `keyed_accounts[1].unsigned_key()` matched `system_id()`.

4. The same area contained a commented TODO about checking account ownership before userdata modification.

5. The bank previously loaded `storage_program::system_id()`, deserialized its `userdata`, and returned `StorageProgramState.entry_height`.

6. The patch changes the storage entrypoint to require one account and deserializes state from `keyed_accounts[0].account.userdata`.

7. The runtime helper and test baseline for the separate storage-system id were removed, consistent with eliminating the global account model.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/native/storage/src/lib.rs | 34 | changes storage instruction account shape from two accounts to one account, removing the separate global storage account parameter |
| programs/native/storage/src/lib.rs | 46 | removes validation and use of `keyed_accounts[1]` as `storage_program::system_id()` and shifts userdata state handling to the signed account |
| runtime/src/bank.rs | 231 | removes bank helper that read storage entry height from the global storage system account userdata |
| runtime/src/bank.rs | 1199 | updates program id test baseline after removing the separate storage system id |

## Code Snippets

## Snippet 1

Context: `runtime/src/bank.rs:231` (changes signature or replay validation logic)

Before
```rust
}

    pub fn get_storage_entry_height(&self) -> u64 {
        match self.get_account(&storage_program::system_id()) {
            Some(storage_system_account) => {
                let state = deserialize(&storage_system_account.userdata);
                if let Ok(state) = state {
                    let state: storage_program::StorageProgramState = state;
```
After
```rust
}

    /// Forget all signatures. Useful for benchmarking.
    pub fn clear_signatures(&self) {
```

## Snippet 2

Context: `programs/native/storage/src/lib.rs:46` (changes an authorization or privilege gate)

Before
```rust
}

    // Following https://github.com/solana-labs/solana/pull/2773,
    // Modifications to userdata can only be made by accounts owned
    // by this program. TODO: Add this check:
    //if !check_id(&keyed_accounts[1].account.owner) {
    //    error!("account[1] is not assigned to the STORAGE_PROGRAM");
    //    Err(ProgramError::InvalidArgument)?;
```
After
```rust
}

    if let Ok(syscall) = bincode::deserialize(data) {
        let mut storage_account_state = if let Ok(storage_account_state) =
            bincode::deserialize(&keyed_accounts[0].account.userdata)
        {
            storage_account_state
```

## Snippet 3

Context: `programs/native/storage/src/lib.rs:34` (changes a sensitive control or state-update path)

Before
```rust
solana_logger::setup();

    if keyed_accounts.len() != 2 {
        // keyed_accounts[1] should be the main storage key
        // to access its userdata
```
After
```rust
solana_logger::setup();

    if keyed_accounts.len() != 1 {
        // keyed_accounts[1] should be the main storage key
        // to access its userdata
```

## Snippet 4

Context: `runtime/src/bank.rs:1199` (changes a sensitive control or state-update path)

Before
```rust
0, 0, 0, 0,
        ]);
        let storage_system = Pubkey::new(&[
            133, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0,
        ]);

        assert_eq!(system_program::id(), system);
```
After
```rust
0, 0, 0, 0,
        ]);

        assert_eq!(system_program::id(), system);
```

# Fix Pattern

Remove the shared global userdata target and bind storage state access to the signed instruction account. Delete runtime/test assumptions that storage state lives under a separate global storage-system account.

## How It Was Fixed

`programs/native/storage/src/lib.rs` was changed from a two-account to a one-account entrypoint, the `keyed_accounts[1]`/`system_id()` validation path was removed, and storage state is now deserialized from `keyed_accounts[0].account.userdata`. `runtime/src/bank.rs` no longer exposes `get_storage_entry_height()` reading from `storage_program::system_id()`, and the separate `storage_system` pubkey test baseline was removed.

# Why It Matters

1. Reduces the chance that unrelated callers can target shared system-account userdata through the storage program.

2. Scopes storage state handling to the signed account participating in the instruction.

3. Removes runtime dependence on storage state stored in a global account.

4. Exploitability and production impact are not established by the provided evidence.

# Evidence Notes

Supported by `programs/native/storage/src/lib.rs` changing the account count from two to one and removing the `keyed_accounts[1]`/`system_id()` path, plus `runtime/src/bank.rs` removing a helper that read `StorageProgramState` from `storage_program::system_id()` userdata. The commit body directly supports an access-control interpretation. However, the provided snippets do not show the full before/after userdata write operation or an adversarial regression test, so high confidence and `confirmed` are too strong. Protocol security invariant: Storage program userdata should be read or modified only through the authorized account participating in the instruction, rather than through a shared global storage/system account that unrelated callers could target. Verification notes: The patch does not prove remote exploitability or describe a concrete attack transaction. The evidence does not show whether ownership checks on `keyed_accounts[0]` were enforced elsewhere. The patch does not prove corruption of consensus state occurred in production. The test evidence shown is only baseline/id coverage, not a full adversarial regression test. No concrete exploit transaction is provided. The full userdata mutation site is not shown in the supplied evidence. Ownership checks for the remaining signed account are not proven by the supplied snippets. The shown test evidence appears to be program-id baseline cleanup, not direct adversarial coverage. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `unauthorized-state-modification`
Final tags: `infrastructure, storage-program, access-control, userdata, account-state-isolation, global-account-removal`

The supplied evidence supports retaining this as security hardening, but not confidently as a concrete security fix. The patch removes a shared/global storage userdata account path, changes the storage program from two accounts to one signed account, and the commit body directly frames the change as preventing other accounts from modifying system-account userdata. However, the snippets do not show the full mutation path, an exploit, or adversarial regression coverage, so `security-fix` is too strong.

## Security Evidence

1. Commit body says other accounts should not be able to modify system account userdata.
2. Storage entrypoint changed from requiring two keyed accounts to one keyed account.
3. Removed code path used `keyed_accounts[1]` as a main storage userdata account tied to `system_id()`.
4. Nearby removed comment notes userdata modification should require ownership by the storage program, but that check was only a TODO.
5. Runtime helper reading storage state from `storage_program::system_id()` userdata was removed.

## Missing Evidence

1. Full before/after userdata write path is not shown.
2. No concrete exploit transaction or attacker-controlled flow is provided.
3. No adversarial regression test is shown in the supplied evidence.
4. Ownership or authorization checks for the remaining signed account are not fully proven by the snippets.

## Claim Boundaries

1. Supports account-state isolation hardening around storage userdata.
2. Does not prove a remotely exploitable vulnerability.
3. Does not prove consensus corruption or production impact.
4. Original `queue` and `signature` tags are not supported by the supplied patch evidence.
5. Best classified as security hardening rather than a confirmed security fix.
