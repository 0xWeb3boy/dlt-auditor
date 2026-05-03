---
case_id: case_20240313_97c481ffb
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: access-control
impact_type:
  - privilege-misuse
confidence: high
source_quality: high
date: 2024-03-13
source_refs:
  - git:97c481ffbc7f1be618fae61c08b88012d3c823ca
  - "src/flamenco/runtime/program/fd_bpf_loader_v4_program.c:505"
  - "src/flamenco/runtime/program/fd_system_program.c:301"
  - "src/flamenco/runtime/fd_account.h:132"
  - "src/flamenco/runtime/info/fd_instr_info.h:51"
tags:
  - blockchain-core
  - transaction-processing
  - access-control
  - writable-account-check
  - account-aliasing
  - privilege-misuse
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes an overly permissive writable-account check in Firedancer's Flamenco runtime. The provided commit message directly states that Firedancer sometimes checked writability by searching for any writable instruction account with the same address, which misbehaved when instruction accounts aliased the same address. The code changes move account helpers toward context plus instruction-account-index APIs so ownership and mutation checks are tied to the specific indexed account entry.

## Observed Patch Facts

1. In `src/flamenco/runtime/program/fd_bpf_loader_v4_program.c`, the patch replaces `Acquire writable handle for program, resize, and copy over data.` with `int err = 0;`.

2. In `src/flamenco/runtime/program/fd_system_program.c`, the patch replaces `if( FD_UNLIKELY( err ) ) return FD_EXECUTOR_INSTR_ERR_FATAL;` with `if( FD_UNLIKELY( err ) ) FD_LOG_ERR(( "fd_instr_borrowed_account_modify_idx failed (%...`.

3. In `src/flamenco/runtime/fd_account.h`, the patch replaces `static inline int` with `int`.

4. In `src/flamenco/runtime/info/fd_instr_info.h`, the patch replaces `/* fd_instr_acc_is_owned_by_current_program returns 1 if the given` with `FD_PROTOTYPES_END`.

## Project Context

The changed code sits primarily in `src/flamenco/runtime/program`, `src/flamenco/runtime`, `src/flamenco`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/flamenco/runtime/program/fd_system_program_nonce.c`, `src/flamenco/runtime/program/fd_config_program.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/flamenco/runtime/program/fd_system_program_nonce.c`, `src/flamenco/runtime/program/fd_config_program.c`. The strongest project-level identifiers around this patch are `account`, `source`, `program`, and `owner`. Nearby tests or test-like files include `src/flamenco/runtime/tests/fd_exec_test.proto`, `src/flamenco/runtime/tests/fd_exec_test.pb.h`.

## Before/After Behavior

Before the patch, helpers such as fd_account_set_owner accepted account metadata and pubkey, and the commit says writable checks could be address-based across instruction accounts. In aliasing cases, a writable entry for an address could satisfy checks for another readonly entry with the same address. After the patch, fd_account_set_owner takes ctx plus instr_acc_idx, and call sites such as fd_system_program_assign pass the account index. The BPF loader deploy path also changes account mutation plumbing to use an indexed account path instead of raw account fields.

# Root Cause

The root cause was loss of instruction-account-index context during authorization. Address-based lookup treated account identity as enough to determine writability, but Solana-style instruction privileges are attached to each instruction-account entry, not merely to the account address.

## Walkthrough

1. An instruction may contain multiple account entries that refer to the same account address.

2. The commit message states Firedancer sometimes checked whether an account was writable by iterating until it found a writable account with the same address.

3. That behavior is overly permissive when one alias is writable and another alias is readonly.

4. The old fd_account_set_owner API accepted account metadata and pubkey, which did not preserve the exact instruction-account index at the helper boundary.

5. The system program assign path previously called fd_account_set_owner with account->meta and account->pubkey.

6. The patch changes fd_account_set_owner to accept ctx and instr_acc_idx, and fd_system_program_assign now passes acct_idx.

7. The BPF loader deploy path is also adjusted so mutation-related helpers receive the program account index rather than only raw account fields.

8. These changes make writable checks index-based, matching the per-instruction-account privilege model.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/flamenco/runtime/fd_account.c | 1 | central account helper implementation now receives instruction account index for owner changes and indexed permission checks |
| src/flamenco/runtime/fd_account.h | 132 | account helper API changed from metadata/pubkey-based checks to context plus instruction-account index |
| src/flamenco/runtime/program/fd_system_program.c | 301 | system program assign path calls fd_account_set_owner by instruction account index after writable acquire |
| src/flamenco/runtime/program/fd_bpf_loader_v4_program.c | 505 | BPF loader deploy path updates writable handle acquisition and account data transfer behavior |
| src/flamenco/runtime/info/fd_instr_info.h | 51 | instruction account helper code involved in address-based signer/writable-style lookup was removed or relocated |

## Code Snippets

## Snippet 1

Context: `src/flamenco/runtime/program/fd_bpf_loader_v4_program.c:505` (changes a sensitive control or state-update path)

Before
```c
/* https://github.com/solana-labs/solana/blob/v1.17.25/programs/loader-v4/src/lib.rs#L432
       Acquire writable handle for program, resize, and copy over data.
       NOTE: This effectively moves the source account's data region
             entirely to the destination account and could therefore be
             done zero-copy. */
    do {
      int err = fd_instr_borrowed_account_modify_idx( &ctx, 0, source->const_meta->dlen, &program );
```
After
```c
/* https://github.com/solana-labs/solana/blob/v1.17.25/programs/loader-v4/src/lib.rs#L432
       NOTE: This effectively moves the source account's data region
             entirely to the destination account and could therefore be
             done zero-copy. */

    do {
      int err = 0;
```

## Snippet 2

Context: `src/flamenco/runtime/program/fd_system_program.c:301` (changes an authorization or privilege gate)

Before
```c
do {
    int err = fd_instr_borrowed_account_modify_idx( ctx, (uchar)acct_idx, 0UL, &account );
    if( FD_UNLIKELY( err ) ) return FD_EXECUTOR_INSTR_ERR_FATAL;
  } while(0);

  return fd_account_set_owner( ctx, account->meta, account->pubkey, owner );
}
```
After
```c
do {
    int err = fd_instr_borrowed_account_modify_idx( ctx, (uchar)acct_idx, 0UL, &account );
    if( FD_UNLIKELY( err ) ) FD_LOG_ERR(( "fd_instr_borrowed_account_modify_idx failed (%d-%s)", err, fd_acc_mgr_strerror( err ) ));
  } while(0);

  return fd_account_set_owner( ctx, acct_idx, owner );
}
```

## Snippet 3

Context: `src/flamenco/runtime/fd_account.h:132` (changes an authorization or privilege gate)

Before
```c
}

static inline int
fd_account_set_owner( fd_exec_instr_ctx_t * ctx,
                      fd_account_meta_t *   acct,
                      fd_pubkey_t const *   key,
                      fd_pubkey_t const *   owner ) {
```
After
```c
}

int
fd_account_set_owner( fd_exec_instr_ctx_t * ctx,
                      ulong                 instr_acc_idx,
                      fd_pubkey_t const *   owner );

/* fd_account_get_lamports mirrors Anza function
```

## Snippet 4

Context: `src/flamenco/runtime/info/fd_instr_info.h:51` (changes an authorization or privilege gate)

Before
```c
}

/* fd_instr_acc_is_owned_by_current_program returns 1 if the given
   account is owned by the program invoked in the current instruction.
   Otherwise, returns 0.  Mirrors Anza's
   solana_sdk::transaction_context::BorrowedAccount::is_owned_by_current_program */

static inline int
```
After
```c
}

FD_PROTOTYPES_END
```

# Fix Pattern

Replace address/meta-based writable authorization with index-based authorization. Account mutation helpers should receive the execution context and instruction-account index, then enforce writability and ownership for that exact entry.

## How It Was Fixed

The patch changes fd_account_set_owner from a static inline helper taking account metadata and pubkey to a function taking ctx, instr_acc_idx, and owner. Call sites were updated to pass the instruction-account index. Related writable handle and account data transfer paths were adjusted to carry indexed account context, including in the BPF loader deploy path.

# Why It Matters

1. Prevents a writable alias from authorizing mutation through a readonly alias.

2. Preserves per-instruction account privilege semantics.

3. Protects owner changes and loader mutations from overly broad writable checks.

4. Provides a focused regression target for aliased account entries.

# Evidence Notes

The strongest evidence is the commit message, which explicitly names an overly permissive writable check and explains the aliasing failure mode. The fd_account.h, fd_system_program.c, and fd_bpf_loader_v4_program.c hunks support the API shift from raw account metadata/pubkey toward instruction-account indices. The evidence does not prove theft, lamport loss, or consensus divergence, so those impacts should not be claimed. Protocol security invariant: Account mutation permissions must be checked against the exact instruction-account index being modified. If the same account address appears at multiple instruction-account indices, writability on one alias must not authorize mutation through a readonly alias. Verification notes: No exploit transaction or attacker-controlled reproduction is shown in the provided evidence. No theft, unauthorized lamport transfer, or consensus divergence is proven by the patch alone. The evidence supports incorrect writable authorization with aliased instruction accounts, not a broader authentication bypass. The exact behavior of every modified call site is not shown; classification is limited to the supplied hunks and commit context. Some changes are API movement/refactoring, but they are security-relevant only where they enforce indexed writability. No exploit transaction is provided. No concrete loss scenario is shown. Security classification rests on the explicit writable-check bug description and matching authorization-path code changes. Helper-file movement appears to be support work, not the root cause by itself. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final tags: `blockchain-core, transaction-processing, access-control, writable-account-check, account-aliasing, privilege-misuse`

The supplied evidence supports retaining this as a security fix. The commit message explicitly identifies an overly permissive writable-account check and readonly-account writable handle acquisition caused by aliased instruction accounts, and the patch changes account mutation helpers to carry the execution context plus instruction-account index rather than raw account metadata/pubkey. In a blockchain runtime, writability is an authorization property, so correcting alias-sensitive writable checks is a concrete access-control fix, not merely cleanup.

## Security Evidence

1. Commit body explicitly says it fixes an overly permissive writable check.
2. Commit body describes the failure mode: aliased instruction accounts with the same address could be mishandled.
3. Commit body says writable handles were acquired on readonly accounts.
4. fd_account_set_owner API changes from metadata/pubkey inputs to ctx plus instruction account index.
5. System program assign path now passes acct_idx into fd_account_set_owner.
6. BPF loader mutation path is updated away from raw account-field plumbing toward indexed account handling.

## Missing Evidence

1. No exploit transaction or reproduction is provided.
2. No concrete asset theft, lamport loss, or consensus impact is shown.
3. The supplied hunks do not show the full new fd_account_set_owner implementation checks.
4. Some patch content is refactoring or file movement rather than independently security-relevant.

## Claim Boundaries

1. Supported claim: writable authorization could be too permissive for aliased instruction accounts.
2. Supported claim: the fix ties mutation checks to the specific instruction-account index.
3. Do not claim signature verification bypass; the evidence is about writable/account mutation privileges.
4. Do not claim proven fund loss or consensus divergence from the supplied patch alone.
