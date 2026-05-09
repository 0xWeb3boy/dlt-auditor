---
case_id: case_20210528_a3240aebde
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
confidence: high
source_quality: high
date: 2021-05-28
source_refs:
  - git:a3240aebdebeb576d421d9f0724503ba6811ef89
  - "runtime/src/message_processor.rs:450"
  - "programs/bpf_loader/src/serialization.rs:453"
  - "programs/bpf_loader/src/serialization.rs:133"
  - "programs/bpf/c/src/invoke/invoke.c:505"
bug_class: read-only-account-mutation
impact_type:
  - state-integrity
tags:
  - blockchain-core
  - bpf-loader
  - cpi
  - read-only-account
  - access-control
  - state-integrity
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch is a security fix for Solana BPF/CPI account handling. It strengthens detection of programs modifying read-only accounts by changing account lookup to prefer pre-instruction account state and by removing a deserialization path that skipped read-only account fields.

## Observed Patch Facts

1. In `runtime/src/message_processor.rs`, the patch replaces `if self.is_feature_active(&cpi_share_ro_and_exec_accounts::id()) {` with `if let Some(account) = self.pre_accounts.iter().find_map(|pre| {`.

2. In `programs/bpf_loader/src/serialization.rs`, the patch replaces `assert_eq!(account.lamports(), de_keyed_account.lamports().unwrap());` with `assert_eq!(account.executable(), de_keyed_account.executable().unwrap());`.

3. In `programs/bpf_loader/src/serialization.rs`, the patch replaces `if keyed_account.is_writable() || !skip_ro_deserialization {` with `.set_lamports(LittleEndian::read_u64(&buffer[start..]));`.

4. In `programs/bpf/c/src/invoke/invoke.c`, the patch replaces `default:` with `case TEST_WRITABLE_DEESCALATION_WRITABLE: {`.

## Project Context

The changed code sits primarily in `runtime/src`, `programs/bpf_loader/src`, `programs/bpf_loader`, which anchors the finding in the `consensus` area of the project. Historical context from `runtime/src/read_only_accounts_cache.rs`, `runtime/src/accounts_db.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/read_only_accounts_cache.rs`, `runtime/src/bank.rs`. The strongest project-level identifiers around this patch are `account`, `start`, `size_of`, and `assert_eq`.

## Before/After Behavior

Before the patch, `InvokeContext::get_account()` could consult feature-gated executable accounts or account dependencies before the pre-instruction account entry, and unaligned BPF parameter deserialization skipped portions of read-only account processing when `skip_ro_deserialization` applied. After the patch, account lookup first searches `pre_accounts`, and deserialization advances through account fields for every non-duplicate account regardless of writability. Tests/regression code were updated around writable de-escalation and read-only account mutation handling.

# Root Cause

The supported root cause is inconsistent read-only account state handling in BPF/CPI execution paths: account lookup did not always prioritize the original pre-instruction account object, and BPF parameter deserialization could skip read-only account fields, weakening the runtime's ability to observe attempted modifications.

## Walkthrough

1. A BPF program or CPI frame receives an account that is read-only for that call.

2. Pre-patch deserialization could skip processing read-only account fields under the `keyed_account.is_writable() || !skip_ro_deserialization` condition.

3. Pre-patch account lookup could prefer feature-gated executable/shared dependency accounts before checking `pre_accounts`.

4. Those behaviors could prevent the runtime comparison path from reliably seeing that a read-only account was changed.

5. The patch makes lookup prefer `pre_accounts` and deserializes non-duplicate account fields regardless of writability.

6. The added regression coverage exercises CPI writable de-escalation where an account is passed as non-writable and a write attempt is made.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/message_processor.rs | 450 | InvokeContext account lookup now uses pre-instruction accounts for state comparison instead of feature-gated shared executable/dependency accounts. |
| programs/bpf_loader/src/serialization.rs | 133 | BPF parameter deserialization now processes account fields even for read-only accounts, making attempted mutations visible to runtime checks. |
| programs/bpf_loader/src/serialization.rs | 453 | Serialization tests updated around read-only account field expectations after deserialization behavior changed. |
| programs/bpf/c/src/invoke/invoke.c | 505 | Regression program adds CPI writable de-escalation coverage for attempts to write through a read-only account meta. |

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

Anchor mutation checks to pre-instruction account state and avoid skipping read-only account deserialization when those fields are needed for enforcement.

## How It Was Fixed

`runtime/src/message_processor.rs` now searches `pre_accounts` first in `get_account()`. `programs/bpf_loader/src/serialization.rs` removes the writability/skip guard around unaligned account field deserialization. BPF/CPI regression coverage was added for writable de-escalation, and serialization test expectations were adjusted.

# Why It Matters

1. Enforces the read-only account access-control invariant.

2. Covers CPI writable de-escalation, an important privilege boundary.

3. Prevents attempted read-only mutations from being masked by deserialization/account lookup behavior.

4. Evidence does not establish fund theft, in-the-wild exploitation, or cryptographic impact.

# Evidence Notes

The commit title, `Always bail if program modifies a ro account (#17569)`, directly states the intended security behavior. The strongest evidence is the `get_account()` change in `runtime/src/message_processor.rs`, removal of the read-only deserialization skip condition in `programs/bpf_loader/src/serialization.rs`, and added CPI writable-deescalation regression code in `programs/bpf/c/src/invoke/invoke.c`. Claims about practical exploitability, fund theft, replay, or cryptographic impact are not supported by the provided evidence. Protocol security invariant: Accounts marked read-only for an instruction or CPI frame must not be modified by the executing program, and runtime/BPF-loader handling must preserve or reconstruct enough account state to detect and fail such attempted modifications. Verification notes: The patch does not by itself prove practical exploitability or fund theft. The evidence does not show consensus divergence being triggered in the wild. The patch does not prove cryptographic or replay logic was affected despite heuristic flags. The exact pre-patch failure mode is inferred from changed account lookup and deserialization behavior, not from a full advisory. Supported by implementation changes in runtime account lookup and BPF loader deserialization. Supported by regression coverage for CPI writable de-escalation. Exact exploit scenario and real-world impact are not proven by the provided input. Helper/test changes are treated as supporting evidence, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `read-only-account-mutation`
Final impact type: `state-integrity`
Final tags: `blockchain-core, bpf-loader, cpi, read-only-account, access-control, state-integrity`

The supplied evidence supports keeping this as a security fix. The commit title directly states that programs modifying read-only accounts must always bail, and the patch changes runtime/BPF account lookup and deserialization behavior in paths that enforce account mutability. Added writable-deescalation regression code further supports that the fix targets a privilege boundary rather than ordinary maintenance. The original consensus/state-corruption framing is somewhat broader than the evidence, so the final classification should focus on read-only account mutation and state integrity.

## Security Evidence

1. Commit subject says the fix is to always bail if a program modifies a read-only account.
2. Runtime account lookup now prefers pre-instruction account state before account dependencies.
3. BPF loader deserialization no longer skips account field processing based on read-only writability handling.
4. Regression code exercises CPI writable deescalation with an attempted write through a non-writable account meta.

## Missing Evidence

1. No advisory or explicit vulnerability disclosure is provided.
2. No proof of in-the-wild exploitation is provided.
3. No evidence establishes fund theft, cryptographic breakage, replay impact, or consensus divergence.

## Claim Boundaries

1. Supported claim: the patch enforces read-only account mutation detection in BPF/CPI execution paths.
2. Supported claim: the bug affects a security-sensitive account mutability invariant.
3. Unsupported claim: practical exploitability or monetary loss.
4. Unsupported claim: cryptographic or replay-sensitive behavior was affected.
