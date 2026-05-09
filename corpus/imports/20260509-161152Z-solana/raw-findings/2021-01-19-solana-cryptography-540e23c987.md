---
case_id: case_20210119_540e23c987
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2021-01-19
source_refs:
  - git:540e23c987a7207a735cf206f23d1fdaa183a082
  - "programs/bpf_loader/src/lib.rs:402"
  - "sdk/program/src/bpf_loader_upgradeable.rs:251"
  - "programs/bpf_loader/src/lib.rs:2119"
  - "sdk/program/src/bpf_loader_upgradeable.rs:183"
bug_class: account-locking-invariant
impact_type:
  - runtime-integrity
tags:
  - blockchain-core
  - bpf-loader
  - upgradeable-loader
  - account-locking
  - transaction-batch
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Solana's upgradeable BPF loader by requiring the executable program account to be writable during Upgrade processing and by changing the SDK Upgrade instruction builder to mark that account writable. This supports the stated goal of preventing program invocation and upgrade in the same transaction batch. The evidence supports account-locking and loader hardening, not unauthorized upgrade, signature bypass, replay, or cryptographic failure.

## Observed Patch Facts

1. In `programs/bpf_loader/src/lib.rs`, the patch replaces `if &program.owner()? != program_id {` with `if !program.is_writable()`.

2. In `sdk/program/src/bpf_loader_upgradeable.rs`, the patch adds `#[test]`.

3. In `programs/bpf_loader/src/lib.rs`, the patch adds `&[`.

4. In `sdk/program/src/bpf_loader_upgradeable.rs`, the patch replaces `AccountMeta::new_readonly(*program_address, false),` with `AccountMeta::new(*program_address, false),`.

## Project Context

The changed code sits primarily in `programs/bpf_loader/src`, `programs/bpf_loader`, `sdk/program/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `programs/bpf_loader/src/syscalls.rs`, `sdk/program/src/system_instruction.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `programs/bpf_loader/src/syscalls.rs`, `sdk/program/src/system_instruction.rs`. The strongest project-level identifiers around this patch are `AccountMeta::new`, `KeyedAccount::new`, `KeyedAccount`, and `AccountMeta`.

## Before/After Behavior

Before the patch, the SDK `upgrade()` helper emitted the executable program account as read-only, and the provided loader snippet does not show a writable-account requirement in the upgrade path. After the patch, the SDK emits the program account as writable, and the loader rejects a non-writable program account with `InstructionError::InvalidArgument` when `prevent_upgrade_and_invoke` is active.

# Root Cause

The upgrade path did not require the executable program account itself to be writable, so an Upgrade instruction could be represented as only a read reference to the program account. That weakened the account-locking signal needed to conflict with simultaneous or same-batch invocation.

## Walkthrough

1. The SDK builds Upgrade instructions in `sdk/program/src/bpf_loader_upgradeable.rs::upgrade`.

2. Before the change, the program account meta was `AccountMeta::new_readonly(*program_address, false)`.

3. The loader upgrade path checked that the program account was executable, but the provided pre-patch snippet does not show a writable-account gate.

4. The patch changes the SDK helper to use `AccountMeta::new(*program_address, false)` for the program account.

5. The loader now checks `program.is_writable()` when the `prevent_upgrade_and_invoke` feature is active.

6. If the program account is not writable, the loader logs `Program account not writeable` and returns `InstructionError::InvalidArgument`.

7. Loader tests were updated to pass the program account as writable in upgrade-processing cases.

8. SDK tests were added around identifying upgrade instructions.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/lib.rs | 402 | loader-side guard rejects upgrade instruction when the program account is not writable while the prevent_upgrade_and_invoke feature is active |
| sdk/program/src/bpf_loader_upgradeable.rs | 183 | SDK upgrade instruction builder marks the program account writable so transactions take the required write lock |
| programs/bpf_loader/src/lib.rs | 2119 | loader tests updated to pass the program account as writable in upgrade processing cases |
| sdk/program/src/bpf_loader_upgradeable.rs | 251 | tests cover identification of upgrade instructions used by the loader/runtime logic |

## Code Snippets

## Snippet 1

Context: `programs/bpf_loader/src/lib.rs:402` (changes a sensitive control or state-update path)

Before
```rust
return Err(InstructionError::AccountNotExecutable);
            }
            if &program.owner()? != program_id {
                log!(logger, "Program account not owned by loader");
```
After
```rust
return Err(InstructionError::AccountNotExecutable);
            }
            if !program.is_writable()
                && invoke_context.is_feature_active(&prevent_upgrade_and_invoke::id())
            {
                log!(logger, "Program account not writeable");
                return Err(InstructionError::InvalidArgument);
            }
```

## Snippet 2

Context: `sdk/program/src/bpf_loader_upgradeable.rs:251` (changes persisted or aggregate state handling)

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
    fn test_is_upgrade_instruction() {
        assert_eq!(
            false,
            is_upgrade_instruction(
```

## Snippet 3

Context: `programs/bpf_loader/src/lib.rs:2119` (changes the branch that decides whether execution stops or continues)

Before
```rust
assert_eq!(
            Err(InstructionError::IncorrectProgramId),
            process_instruction(
                &bpf_loader_upgradeable::id(),
```
After
```rust
assert_eq!(
            Err(InstructionError::IncorrectProgramId),
            process_instruction(
                &bpf_loader_upgradeable::id(),
                &[
                    KeyedAccount::new(&programdata_address, false, &programdata_account),
                    KeyedAccount::new(&program_address, false, &program_account),
                    KeyedAccount::new(&buffer_address, false, &buffer_account),
```

## Snippet 4

Context: `sdk/program/src/bpf_loader_upgradeable.rs:183` (changes a sensitive control or state-update path)

Before
```rust
vec![
            AccountMeta::new(programdata_address, false),
            AccountMeta::new_readonly(*program_address, false),
            AccountMeta::new(*buffer_address, false),
            AccountMeta::new(*spill_address, false),
```
After
```rust
vec![
            AccountMeta::new(programdata_address, false),
            AccountMeta::new(*program_address, false),
            AccountMeta::new(*buffer_address, false),
            AccountMeta::new(*spill_address, false),
```

# Fix Pattern

Mark the execution-bearing program account writable for upgrade instructions and enforce the same requirement in the loader under a feature gate.

## How It Was Fixed

The SDK Upgrade instruction builder was changed from a read-only program account meta to a writable program account meta. The upgradeable BPF loader added a feature-gated `program.is_writable()` validation and rejects non-writable program accounts during Upgrade processing.

# Why It Matters

1. Preserves separation between program execution and program replacement.

2. Uses account writability to express the runtime conflict explicitly.

3. Prevents upgrades from looking like read-only references to executable program accounts.

4. Does not establish unauthorized upgrade, signature bypass, replay, or funds theft.

# Evidence Notes

Strong evidence: `programs/bpf_loader/src/lib.rs` adds the feature-gated `program.is_writable()` guard, and `sdk/program/src/bpf_loader_upgradeable.rs` changes the Upgrade instruction's program account from read-only to writable. The same-batch invoke/upgrade purpose is directly stated by the commit subject and body, but detailed scheduler behavior is inferred from writability/account-locking semantics rather than fully shown in the snippets. Protocol security invariant: An upgradeable BPF program should not be invoked in the same transaction processing batch in which it is upgraded. Upgrade processing should require the executable program account to be writable so runtime account-locking/conflict rules can separate execution from replacement. Verification notes: The patch does not prove unauthorized program upgrade was possible. The patch does not prove signature validation, replay protection, or cryptographic verification was defective. The patch does not prove remote exploitability or funds theft from the provided evidence. The exact same-transaction versus same-batch scheduler behavior is inferred from the commit message and writable-account enforcement, not fully demonstrated by the snippets. Code evidence supports the loader and SDK behavior change. Commit message supports the intended same-batch invoke/upgrade prevention. No evidence supports cryptography, replay, signature-validation, or unauthorized-upgrade claims. Confidence is medium because the account-locking security impact is inferred from the provided snippets plus the commit message. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `account-locking-invariant`
Final impact type: `runtime-integrity`
Final tags: `blockchain-core, bpf-loader, upgradeable-loader, account-locking, transaction-batch, security-hardening`

The supplied evidence supports retaining this as security hardening: the commit explicitly prevents invoking and upgrading a program in the same transaction batch, and the patch enforces that upgrade instructions require the executable program account to be writable so account-locking can create a conflict. The evidence does not support the original cryptography, replay, or signature-validation framing, nor does it prove a concrete exploitable unauthorized-upgrade vulnerability.

## Security Evidence

1. Loader upgrade processing now rejects a non-writable program account when the prevent_upgrade_and_invoke feature is active.
2. The SDK upgrade instruction builder changed the program account from read-only to writable.
3. The commit subject and body directly state the intended invariant: prevent invoke and upgrade of programs in the same transaction batch.
4. Tests were updated around upgrade instruction handling and writable program accounts.

## Missing Evidence

1. No direct exploit scenario is shown.
2. No evidence shows unauthorized upgrade, signature bypass, replay, or cryptographic failure.
3. The snippets do not fully demonstrate the transaction scheduler or account-locking behavior.
4. No impact such as funds loss, privilege escalation, or consensus failure is proven from the patch alone.

## Claim Boundaries

1. Valid claim: loader and SDK harden upgrade handling by requiring the program account to be writable.
2. Valid claim: the change is intended to prevent same-batch invoke and upgrade behavior.
3. Do not classify this as cryptography, replay, or signature validation.
4. Do not claim a proven concrete vulnerability beyond security-sensitive runtime hardening.
