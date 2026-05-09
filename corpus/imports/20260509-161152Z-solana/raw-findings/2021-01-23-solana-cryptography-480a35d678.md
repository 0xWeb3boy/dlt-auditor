---
case_id: case_20210123_480a35d678
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
impact_type:
  - state-integrity
confidence: medium
source_quality: high
date: 2021-01-23
source_refs:
  - git:480a35d6785c4fb961bd1df341583f9617fa549a
  - "runtime/src/message_processor.rs:809"
  - "runtime/benches/message_processor.rs:17"
  - "runtime/benches/message_processor.rs:42"
  - "programs/bpf_loader/src/syscalls.rs:1563"
bug_class: improper-privilege-propagation
tags:
  - blockchain-core
  - access-control
  - cpi
  - account-writability
  - privilege-deescalation
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds tracking for account writable deescalation in Solana runtime/BPF CPI execution. The strongest supported claim is that writable privilege context is now threaded into post-instruction account verification paths so account changes can be checked against the caller-effective writable status.

## Observed Patch Facts

1. In `runtime/src/message_processor.rs`, the patch replaces `// Find the matching PreAccount` with `let is_writable = if track_writable_deescalation {`.

2. In `runtime/benches/message_processor.rs`, the patch replaces `true,` with `assert_eq!(`.

3. In `runtime/benches/message_processor.rs`, the patch replaces `true,` with `pre.verify(&non_owner, Some(false), &Rent::default(), &post)`.

4. In `programs/bpf_loader/src/syscalls.rs`, the patch replaces `if invoke_context.is_feature_active(&limit_cpi_loader_invoke::id()) {` with `let caller_privileges = message`.

## Project Context

The changed code sits primarily in `runtime/src`, `runtime/benches`, `programs/bpf_loader/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `runtime/src/bank.rs`, `runtime/src/accounts.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `runtime/src/accounts.rs`. The strongest project-level identifiers around this patch are `Rent::default`, `Account::new`, `pubkey::new_rand`, and `owner`.

## Before/After Behavior

Before the change, the provided `verify_and_update` evidence does not show local computation of an effective writable flag before account verification, and the BPF syscall path does not show caller writable privileges being captured after creating the callee message. After the change, `verify_and_update` computes an optional writable value from `caller_privileges` or `message.is_writable(account_index)`, while the BPF syscall path maps callee account keys back to caller `KeyedAccount` writability and defaults unmatched accounts to read-only. Benchmark call sites show `PreAccount::verify` now accepts an explicit writable option.

# Root Cause

The supported root cause is missing or insufficient propagation of effective writable privilege into account verification, especially for CPI paths where caller privileges may differ from callee message metadata. The exact rejected mutation condition is not shown in the provided evidence because the full `PreAccount::verify` implementation is absent.

## Walkthrough

1. A BPF CPI call creates a callee message from instruction data and caller keyed accounts.

2. The patch derives `caller_privileges` by matching each callee account key to the caller's keyed accounts and reading `is_writable()`.

3. Unmatched callee keys are treated as not writable in that derived privilege list.

4. `MessageProcessor::verify_and_update` now computes an optional writable context when writable-deescalation tracking is enabled.

5. That writable context is tied to either caller privileges or message writability, depending on whether caller privileges are available.

6. Updated benchmark call sites show the verification interface now takes an explicit writable option.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/message_processor.rs | 795 | verifies per-account post-instruction changes using tracked writable/deescalation context |
| runtime/src/message_processor.rs | 809 | derives effective writable flag from caller privileges or message writability before account verification |
| programs/bpf_loader/src/syscalls.rs | 1522 | BPF CPI syscall entry point that constructs the callee message and captures caller account writability |
| programs/bpf_loader/src/syscalls.rs | 1563 | maps CPI account keys to caller writable privileges for downstream verification |
| runtime/benches/message_processor.rs | 11 | updated benchmark coverage for `PreAccount::verify` with explicit writable option |
| runtime/benches/message_processor.rs | 42 | updated non-owner account verification benchmark with explicit writable option |

## Code Snippets

## Snippet 1

Context: `runtime/src/message_processor.rs:809` (changes a sensitive control or state-update path)

Before
```rust
let key = &message.account_keys[account_index];
                let account = &accounts[account_index];
                // Find the matching PreAccount
                for pre_account in pre_accounts.iter_mut() {
```
After
```rust
let key = &message.account_keys[account_index];
                let account = &accounts[account_index];
                let is_writable = if track_writable_deescalation {
                    Some(if let Some(caller_privileges) = caller_privileges {
                        caller_privileges[account_index]
                    } else {
                        message.is_writable(account_index)
                    })
```

## Snippet 2

Context: `runtime/benches/message_processor.rs:17` (changes an authorization or privilege gate)

Before
```rust
&pubkey::new_rand(),
        &Account::new(0, BUFSIZE, &owner),
        true,
        false,
    );
    let post = Account::new(0, BUFSIZE, &owner);
    assert_eq!(pre.verify(&owner, &Rent::default(), &post), Ok(()));
```
After
```rust
&pubkey::new_rand(),
        &Account::new(0, BUFSIZE, &owner),
        false,
    );
    let post = Account::new(0, BUFSIZE, &owner);
    assert_eq!(
        pre.verify(&owner, Some(false), &Rent::default(), &post),
        Ok(())
```

## Snippet 3

Context: `runtime/benches/message_processor.rs:42` (changes signature or replay validation logic)

Before
```rust
&pubkey::new_rand(),
        &Account::new(0, BUFSIZE, &owner),
        true,
        false,
    );
    bencher.iter(|| {
        pre.verify(&non_owner, &Rent::default(), &post).unwrap();
    });
```
After
```rust
&pubkey::new_rand(),
        &Account::new(0, BUFSIZE, &owner),
        false,
    );
    bencher.iter(|| {
        pre.verify(&non_owner, Some(false), &Rent::default(), &post)
            .unwrap();
    });
```

## Snippet 4

Context: `programs/bpf_loader/src/syscalls.rs:1563` (changes a sensitive control or state-update path)

Before
```rust
MessageProcessor::create_message(&instruction, &keyed_account_refs, &signers)
                .map_err(SyscallError::InstructionError)?;
        if invoke_context.is_feature_active(&limit_cpi_loader_invoke::id()) {
            check_authorized_program(&callee_program_id, &instruction.data)?;
```
After
```rust
MessageProcessor::create_message(&instruction, &keyed_account_refs, &signers)
                .map_err(SyscallError::InstructionError)?;
        let caller_privileges = message
            .account_keys
            .iter()
            .map(|key| {
                if let Some(keyed_account) = keyed_account_refs
                    .iter()
```

# Fix Pattern

Propagate effective authorization state across the CPI/runtime boundary and use it during post-instruction account verification.

## How It Was Fixed

The runtime added `track_writable_deescalation` and `caller_privileges` handling in `MessageProcessor::verify_and_update`. The BPF loader syscall path now constructs a caller-writability list for callee message accounts. Supporting call sites were updated for the new `PreAccount::verify` interface that accepts an explicit writable context.

# Why It Matters

1. Writable status is an account mutation authorization boundary.

2. CPI privilege deescalation must survive message construction and verification.

3. The patch affects runtime and BPF loader paths, not just tests or cleanup.

4. The evidence does not support stronger claims such as cryptographic failure, fund theft, or arbitrary state corruption.

# Evidence Notes

Primary evidence is `runtime/src/message_processor.rs`, where `verify_and_update` computes `is_writable` from `caller_privileges` or `message.is_writable`. CPI evidence is `programs/bpf_loader/src/syscalls.rs`, where caller writable privileges are derived from caller keyed accounts. Benchmark evidence only supports the changed verification interface. The provided evidence does not include the full `PreAccount::verify` implementation or a failing regression test, so confidence is medium rather than high. Protocol security invariant: Account mutation checks during instruction and CPI execution should use the effective writable privilege for that invocation, including any writable deescalation from the caller, rather than relying only on broader message-level writability. Verification notes: The patch does not show cryptographic logic being changed. The patch does not by itself prove remote exploitability or fund theft. The patch does not prove arbitrary state corruption beyond account mutation privilege handling. Benchmark updates are supporting evidence only, not the security fix itself. The provided evidence does not show the full `PreAccount::verify` implementation, so the exact rejection condition is inferred from call-path changes and commit subject. Do not classify this as cryptography; no cryptographic code change is shown. Do not claim confirmed exploitability or asset theft from the provided evidence. Benchmark changes are support code, not the root cause. Security relevance is likely because the patch changes runtime account privilege enforcement. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-privilege-propagation`
Final tags: `blockchain-core, access-control, cpi, account-writability, privilege-deescalation, state-integrity`

The supplied patch evidence supports retaining this as security hardening, not a confidently proven security fix. The change propagates caller-effective account writability through BPF CPI and runtime post-instruction verification, including defaulting unmatched accounts to read-only. That is security-sensitive authorization behavior in a blockchain runtime, but the evidence does not include the full rejection logic, a regression test, or proof of an exploitable bypass. The original cryptography/signature/state-corruption framing is too strong and should be narrowed to privilege propagation and account writability enforcement.

## Security Evidence

1. Runtime verification now computes an optional writable flag when writable-deescalation tracking is enabled.
2. BPF CPI syscall code derives caller_privileges by mapping callee account keys back to caller KeyedAccount writability.
3. Unmatched CPI account keys are assigned false writability, a conservative read-only default.
4. PreAccount::verify call sites now accept explicit writable context, indicating account-change checks depend on effective writability.

## Missing Evidence

1. Full PreAccount::verify implementation is not provided, so the exact enforced failure condition is inferred.
2. No failing regression test or exploit scenario is shown in the supplied evidence.
3. No evidence shows cryptographic or signature-validation logic was changed.
4. No proof is supplied that the prior behavior enabled asset theft or arbitrary state corruption.

## Claim Boundaries

1. Classify as account privilege propagation or access-control hardening, not cryptography.
2. Do not claim confirmed exploitability from this patch alone.
3. Do not claim arbitrary state corruption beyond possible improper account mutation authorization.
4. Benchmark changes are supporting interface evidence, not primary security evidence.
