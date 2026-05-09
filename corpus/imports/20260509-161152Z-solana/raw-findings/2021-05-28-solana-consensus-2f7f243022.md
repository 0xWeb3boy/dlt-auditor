---
case_id: case_20210528_2f7f243022
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
impact_type:
  - state-integrity
confidence: high
source_quality: high
date: 2021-05-28
source_refs:
  - git:2f7f243022c731400563f4ca8dfcf978d26eb76b
  - "runtime/src/message_processor.rs:450"
  - "programs/bpf_loader/src/serialization.rs:453"
  - "programs/bpf_loader/src/serialization.rs:133"
  - "programs/bpf/c/src/invoke/invoke.c:505"
bug_class: read-only-account-modification-bypass
tags:
  - blockchain-core
  - bpf-loader
  - account-permissions
  - read-only-account
  - cpi
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes Solana BPF invocation permission enforcement so attempted modifications to read-only accounts are not hidden by deserialization behavior or account lookup source selection.

## Observed Patch Facts

1. In `runtime/src/message_processor.rs`, the patch replaces `if self.is_feature_active(&cpi_share_ro_and_exec_accounts::id()) {` with `if let Some(account) = self.pre_accounts.iter().find_map(|pre| {`.

2. In `programs/bpf_loader/src/serialization.rs`, the patch replaces `assert_eq!(account.lamports(), de_keyed_account.lamports().unwrap());` with `assert_eq!(account.executable(), de_keyed_account.executable().unwrap());`.

3. In `programs/bpf_loader/src/serialization.rs`, the patch replaces `if keyed_account.is_writable() || !skip_ro_deserialization {` with `.set_lamports(LittleEndian::read_u64(&buffer[start..]));`.

4. In `programs/bpf/c/src/invoke/invoke.c`, the patch replaces `default:` with `case TEST_WRITABLE_DEESCALATION_WRITABLE: {`.

## Project Context

The changed code sits primarily in `runtime/src`, `programs/bpf_loader/src`, `programs/bpf_loader`, which anchors the finding in the `consensus` area of the project. Historical context from `runtime/src/read_only_accounts_cache.rs`, `runtime/src/accounts_db.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/read_only_accounts_cache.rs`, `runtime/src/bank.rs`. The strongest project-level identifiers around this patch are `account`, `start`, `size_of`, and `assert_eq`.

## Before/After Behavior

Before the patch, `deserialize_parameters_unaligned` could skip deserializing read-only account state under `skip_ro_deserialization`, which could prevent later checks from observing that a program changed a read-only account buffer. `get_account` also used feature-gated dependency/executable-account lookup before the pre-invocation account snapshot. After the patch, non-duplicate accounts are deserialized regardless of writability, and account lookup prefers `pre_accounts`, supporting detection of read-only account modification attempts.

# Root Cause

The root cause was a validation gap in the BPF loader/CPI account handling path: read-only account changes could be missed when read-only deserialization was skipped, and account lookup did not first anchor checks to the pre-invocation account snapshot.

## Walkthrough

1. A BPF invocation receives account data and can alter its serialized account buffer during execution.

2. Some accounts may be read-only for the current invocation, including accounts passed through CPI with writable privilege deescalated.

3. Before the fix, the deserialization path could skip read-only accounts, so a modified read-only account might not be reconstructed for validation.

4. Before the fix, account lookup could resolve through dependency or executable-account sources before `pre_accounts`, weakening the baseline used for modification checks.

5. The patch removes the read-only skip in non-duplicate account deserialization and makes lookup prefer `pre_accounts`.

6. Regression coverage adds a writable-deescalation case where a callee receives an account as read-only and attempts to modify it.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/serialization.rs | 126 | Deserializes BPF program account buffers back into runtime account state; changed so read-only accounts are still processed, allowing illegal modifications to be detected. |
| programs/bpf_loader/src/serialization.rs | 447 | Updates serialization tests so read-only account lamports/data/owner are not treated as normal post-deserialization changes while metadata remains checked. |
| runtime/src/message_processor.rs | 448 | InvokeContext account lookup now checks pre_accounts first, preserving the correct baseline for account modification checks. |
| programs/bpf/c/src/invoke/invoke.c | 505 | Regression test program adds writable-deescalation scenario where a callee receives an account as read-only and attempts modification. |

## Code Snippets

## Snippet 1

Context: `runtime/src/message_processor.rs:450` (changes a sensitive control or state-update path)

Before
```rust
}
    fn get_account(&self, pubkey: &Pubkey) -> Option<Rc<RefCell<AccountSharedData>>> {
        if self.is_feature_active(&cpi_share_ro_and_exec_accounts::id()) {
            if let Some((_, account)) = self
                .executable_accounts
                .iter()
                .find(|(key, _)| key == pubkey)
            {
```
After
```rust
}
    fn get_account(&self, pubkey: &Pubkey) -> Option<Rc<RefCell<AccountSharedData>>> {
        if let Some(account) = self.pre_accounts.iter().find_map(|pre| {
            if pre.key == *pubkey {
                Some(pre.account.clone())
            } else {
                None
            }
```

## Snippet 2

Context: `programs/bpf_loader/src/serialization.rs:453` (changes an authorization or privilege gate)

Before
```rust
assert_eq!(key, *de_keyed_account.unsigned_key());
            let account = account.borrow();
            assert_eq!(account.lamports(), de_keyed_account.lamports().unwrap());
            assert_eq!(
                account.data(),
                de_keyed_account.try_account_ref().unwrap().data()
            );
            assert_eq!(*account.owner(), de_keyed_account.owner().unwrap());
```
After
```rust
assert_eq!(key, *de_keyed_account.unsigned_key());
            let account = account.borrow();
            assert_eq!(account.executable(), de_keyed_account.executable().unwrap());
            assert_eq!(account.rent_epoch(), de_keyed_account.rent_epoch().unwrap());
```

## Snippet 3

Context: `programs/bpf_loader/src/serialization.rs:133` (changes bounds, limits, or capacity handling)

Before
```rust
start += 1; // is_dup
        if !is_dup {
            if keyed_account.is_writable() || !skip_ro_deserialization {
                start += size_of::<u8>(); // is_signer
                start += size_of::<u8>(); // is_writable
                start += size_of::<Pubkey>(); // key
                keyed_account
                    .try_account_ref_mut()?
```
After
```rust
start += 1; // is_dup
        if !is_dup {
            start += size_of::<u8>(); // is_signer
            start += size_of::<u8>(); // is_writable
            start += size_of::<Pubkey>(); // key
            keyed_account
                .try_account_ref_mut()?
                .set_lamports(LittleEndian::read_u64(&buffer[start..]));
```

## Snippet 4

Context: `programs/bpf/c/src/invoke/invoke.c:505` (changes bounds, limits, or capacity handling)

Before
```c
break;
  }
  default:
    sol_panic();
```
After
```c
break;
  }
  case TEST_WRITABLE_DEESCALATION_WRITABLE: {
  sol_log("Test writable deescalation");
      uint8_t buffer[10];
      for (int i = 0; i < 10; i++) {
        buffer[i] = accounts[INVOKED_ARGUMENT_INDEX].data[i];
      }
```

# Fix Pattern

Deserialize account state needed for validation even when the account is read-only, then compare against the correct pre-invocation baseline and fail on unauthorized modification.

## How It Was Fixed

The serialization code removed the `keyed_account.is_writable() || !skip_ro_deserialization` guard around non-duplicate account deserialization. The invoke context account lookup now checks `pre_accounts` before falling back to account dependencies. Tests were updated and expanded around read-only/writable-deescalated account behavior.

# Why It Matters

1. Preserves the invariant that read-only accounts cannot be modified by programs.

2. Covers CPI writable-deescalation cases.

3. Prevents read-only mutations from being missed by deserialization skipping.

4. Keeps checks tied to the pre-invocation account snapshot.

# Evidence Notes

The strongest evidence is the commit subject, `Always bail if program modifies a ro account`, plus the removal of the read-only deserialization skip in `programs/bpf_loader/src/serialization.rs`, the `pre_accounts` lookup priority in `runtime/src/message_processor.rs`, and the added writable-deescalation regression case in `programs/bpf/c/src/invoke/invoke.c`. The evidence supports an account-permission security fix, but does not establish theft, remote exploit mechanics beyond BPF program-controlled account buffer mutation, or consensus divergence. Protocol security invariant: A BPF program invocation must not be able to modify accounts that were read-only for that invocation. Read-only or writable-deescalated account changes must be detected and cause execution to fail. Verification notes: Patch evidence does not prove theft of lamports or unauthorized committed writes occurred on chain. Patch evidence does not show remote exploitability mechanics beyond program-controlled account buffer mutation during BPF execution. Patch evidence does not establish consensus divergence by itself, only a runtime account-permission invariant failure path. The changed tests demonstrate regression coverage, not the full set of affected instructions or feature-gated deployments. No claim of theft is supported by the supplied evidence. No claim of consensus divergence is supported by the supplied evidence. Helper/test additions support the regression scenario but are not the root cause. Security classification is based on enforced account write permissions in the BPF invocation path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `read-only-account-modification-bypass`
Final tags: `blockchain-core, bpf-loader, account-permissions, read-only-account, cpi`

The supplied patch evidence supports keeping this as a security fix. The commit explicitly targets bailing when a program modifies a read-only account, and the code removes behavior that skipped read-only account deserialization, changes account lookup to prefer the pre-invocation snapshot, and adds a writable-deescalation regression case. This is best framed as a BPF/CPI account-permission enforcement fix rather than a broad consensus or proven theft issue.

## Security Evidence

1. Commit subject says programs must always bail when modifying a read-only account.
2. Deserialization no longer skips non-duplicate read-only accounts, allowing unauthorized mutations to be observed.
3. Invoke account lookup now checks pre_accounts first, tying validation to the pre-invocation account baseline.
4. Regression code adds a writable-deescalation case where an invoked program receives an account as read-only and attempts modification.

## Missing Evidence

1. No evidence of exploited theft or unauthorized committed transfers is provided.
2. No evidence directly proving consensus divergence is provided.
3. No full before/after test assertion output is provided showing the exact failure mode.
4. No deployment or feature-activation impact is established from the supplied evidence.

## Claim Boundaries

1. Validated as an account-permission enforcement security fix in the BPF/CPI path.
2. Do not claim demonstrated fund theft from this evidence alone.
3. Do not claim confirmed consensus failure from this evidence alone.
4. The strongest supported impact is preservation of read-only account state integrity during program invocation.
