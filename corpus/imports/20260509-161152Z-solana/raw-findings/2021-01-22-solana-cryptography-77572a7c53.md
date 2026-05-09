---
case_id: case_20210122_77572a7c53
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2021-01-22
source_refs:
  - git:77572a7c53fbcebec3b43e7c3d43a6904c845bab
  - "runtime/src/message_processor.rs:809"
  - "runtime/benches/message_processor.rs:17"
  - "runtime/benches/message_processor.rs:42"
  - "programs/bpf_loader/src/syscalls.rs:1563"
bug_class: cpi-writable-privilege-tracking
impact_type:
  - access-control
  - state-integrity
tags:
  - blockchain-core
  - cpi
  - writable-privilege
  - access-control
  - runtime-verification
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is likely a security fix for CPI writable privilege tracking. The supplied evidence shows caller account writability being captured in the BPF loader syscall path and passed into runtime account verification, but it does not include the full PreAccount::verify logic, a regression test, or a concrete exploit, so the draft's confirmed/high-confidence claim should be downgraded.

## Observed Patch Facts

1. In `runtime/src/message_processor.rs`, the patch replaces `// Find the matching PreAccount` with `let is_writable = if track_writable_deescalation {`.

2. In `runtime/benches/message_processor.rs`, the patch replaces `true,` with `assert_eq!(`.

3. In `runtime/benches/message_processor.rs`, the patch replaces `true,` with `pre.verify(&non_owner, Some(false), &Rent::default(), &post)`.

4. In `programs/bpf_loader/src/syscalls.rs`, the patch replaces `if invoke_context.is_feature_active(&limit_cpi_loader_invoke::id()) {` with `let caller_privileges = message`.

## Project Context

The changed code sits primarily in `runtime/src`, `runtime/benches`, `programs/bpf_loader/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `runtime/src/bank.rs`, `runtime/src/accounts.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `runtime/src/accounts.rs`. The strongest project-level identifiers around this patch are `Rent::default`, `Account::new`, `pubkey::new_rand`, and `owner`.

## Before/After Behavior

Before the patch, the shown CPI syscall path created the callee message without preserving a per-account caller writability vector, and the shown runtime verification path did not compute an effective writable value from caller privileges. After the patch, syscalls.rs builds caller_privileges from keyed_account.is_writable(), message_processor.rs selects caller_privileges[account_index] when writable-deescalation tracking is enabled, and verification call sites are updated to pass an optional writable-context argument.

# Root Cause

The likely root cause was that CPI post-account verification lacked explicit caller-derived writability context, allowing verification to depend on the callee message's account writability rather than the caller's effective writable privilege. This is an inference from the added caller_privileges plumbing; the supplied evidence does not show the vulnerable PreAccount::verify behavior directly.

## Walkthrough

1. A BPF program enters the CPI syscall path and creates a callee Message from instruction data, caller keyed accounts, and signer data.

2. Before the patch, the supplied syscall hunk does not show a caller_privileges vector being captured.

3. The patch builds caller_privileges by matching message account keys to the caller's keyed accounts and recording keyed_account.is_writable(), defaulting to false when absent.

4. MessageProcessor::verify_and_update now accepts writable-deescalation tracking state and optional caller privileges.

5. When tracking is enabled, runtime verification uses the caller privilege for the account index, or falls back to message.is_writable when caller privileges are unavailable.

6. Benchmarks are updated to pass Some(false) to PreAccount::verify, supporting that verification now receives explicit effective-writability input.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/syscalls.rs | 1563 | captures caller account writable privileges when constructing a CPI message |
| runtime/src/message_processor.rs | 795 | threads caller privilege context into post-instruction account verification |
| runtime/src/message_processor.rs | 809 | selects effective writable status from caller privileges or message writability for verification |
| runtime/benches/message_processor.rs | 17 | updates PreAccount verification callers for the new writable-context argument |
| runtime/benches/message_processor.rs | 42 | updates non-owner account verification benchmark for the new writable-context argument |

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

Capture caller-derived privileges at the CPI boundary and thread them into post-instruction account verification so writable checks are based on effective caller authority.

## How It Was Fixed

The BPF loader syscall constructs a caller_privileges vector from the caller's keyed accounts. The runtime message processor computes an optional is_writable value from that vector when writable-deescalation tracking is active and passes the context into account verification. Supporting callers were updated for the new verification signature.

# Why It Matters

1. CPI account mutation is access-control sensitive.

2. Caller read-only or deescalated account privileges should constrain callees.

3. The evidence supports writable privilege enforcement, not cryptography or generic state corruption.

4. Concrete exploitability and impact are not proven by the supplied snippets.

# Evidence Notes

Primary evidence is the new caller_privileges construction in programs/bpf_loader/src/syscalls.rs and the new is_writable selection in runtime/src/message_processor.rs. Benchmark changes show API propagation only. The supplied evidence does not include the full PreAccount::verify implementation, feature activation semantics, regression tests, or an exploit scenario, so confirmed/high confidence is not justified. Protocol security invariant: During cross-program invocation, account writability used for post-instruction verification should reflect the caller's effective privileges, so a callee cannot be verified as allowed to mutate an account beyond the caller's writable authority. Verification notes: The patch evidence does not prove a concrete exploit transaction. The patch evidence does not show theft, fund loss, or consensus divergence by itself. This is not shown to be a cryptographic flaw despite heuristic labels mentioning cryptography. The supplied evidence does not establish impact outside CPI writable privilege tracking. Bench changes are supporting updates, not primary security evidence. Downgraded security_verdict from confirmed to likely. Downgraded confidence from high to medium. Changed bug class away from cryptography/state-corruption to writable privilege enforcement. Kept in security corpus because the changed path directly concerns CPI account writability and runtime verification. Did not claim theft, fund loss, consensus divergence, or a proven exploit. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cpi-writable-privilege-tracking`
Final impact type: `access-control, state-integrity`
Final tags: `blockchain-core, cpi, writable-privilege, access-control, runtime-verification`

The supplied patch evidence supports retaining this as security hardening: it adds caller-derived writable privilege tracking at the BPF CPI boundary and threads that context into runtime post-account verification. That is clearly security-sensitive access-control behavior. However, the evidence does not show the full verification logic, regression test, feature activation semantics, or an exploit, so it should not be kept as a concrete security-fix claim and the cryptography/signature framing is misleading.

## Security Evidence

1. BPF loader syscall builds caller_privileges from keyed_account.is_writable() for CPI message accounts.
2. MessageProcessor verification now computes is_writable from caller_privileges when writable deescalation tracking is enabled.
3. Updated PreAccount::verify call sites pass explicit writable context, showing the new parameter affects account-change verification.
4. The changed path concerns CPI account mutability and runtime enforcement, which are access-control sensitive in blockchain execution.

## Missing Evidence

1. No full PreAccount::verify implementation is supplied to prove the exact rejected behavior.
2. No regression test or exploit transaction is shown.
3. No evidence demonstrates fund theft, consensus failure, or concrete state corruption.
4. No evidence supports classifying this as cryptography or signature-related.

## Claim Boundaries

1. Validated only as CPI writable privilege enforcement hardening.
2. Do not claim a proven exploitable vulnerability from the supplied patch alone.
3. Do not claim cryptographic failure, signature bypass, or replay impact.
4. State-integrity impact is limited to account mutation authorization context.
