---
case_id: case_20240429_cf108c124
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
source_quality: high
tags:
  - blockchain-core
  - transaction-processing
  - access-control
  - privilege-misuse
  - signature
date: 2024-04-29
source_refs:
  - git:cf108c12439e25ce8da9101c3b570ae38582006e
  - "src/flamenco/runtime/program/fd_bpf_loader_v3_program.c:628"
  - "src/flamenco/runtime/program/fd_bpf_loader_v3_program.c:1019"
  - "src/flamenco/runtime/program/fd_bpf_loader_v3_program.c:1078"
  - "src/flamenco/runtime/program/fd_bpf_loader_v3_program.c:1088"
confidence: medium
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The supported security-relevant change is in `src/flamenco/runtime/program/fd_bpf_loader_v3_program.c`: the deploy path changed its required-signature gate from comparing `instr_acc_idxs[7]` against `ctx.txn_ctx->txn_descriptor->signature_cnt` to directly checking `fd_instr_acc_is_signer_idx(ctx.instr, 7)`. This is grounded evidence of an authorization-check correction in the upgradeable BPF loader. Other supplied hunks are mostly formatting or surrounding context and should not be treated as separate vulnerability fixes.

## Observed Patch Facts

1. In `src/flamenco/runtime/program/fd_bpf_loader_v3_program.c`, the patch replaces `if (!read_bpf_upgradeable_loader_state( &ctx, buffer_acc, &buffer_acc_loader_state, &...` with `if ( !read_bpf_upgradeable_loader_state( &ctx, buffer_acc, &buffer_acc_loader_state,...`.

2. In `src/flamenco/runtime/program/fd_bpf_loader_v3_program.c`, the patch replaces `if (!read_bpf_upgradeable_loader_state( &ctx, loader_acc, &loader_state, &err)) {` with `if ( !read_bpf_upgradeable_loader_state( &ctx, loader_acc, &loader_state, &err ) ) {`.

3. In `src/flamenco/runtime/program/fd_bpf_loader_v3_program.c`, the patch replaces `if (!read_bpf_upgradeable_loader_state( &ctx, close_acc, &loader_state, &err ))` with `if ( !read_bpf_upgradeable_loader_state( &ctx, close_acc, &loader_state, &err ) )`.

4. In `src/flamenco/runtime/program/fd_bpf_loader_v3_program.c`, the patch replaces `if (FD_FEATURE_ACTIVE(ctx.slot_ctx, enable_program_redeployment_cooldown)) {` with `if ( FD_FEATURE_ACTIVE( ctx.slot_ctx, enable_program_redeployment_cooldown ) ) {`.

## Project Context

The changed code sits primarily in `src/flamenco/runtime/program`, `src/flamenco/runtime`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/flamenco/runtime/program/fd_bpf_loader_v3_program.h`, `src/flamenco/runtime/program/fd_vote_program.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/flamenco/runtime/program/fd_bpf_loader_v3_program.h`, `src/flamenco/runtime/fd_executor.c`. The strongest project-level identifiers around this patch are `loader_state`, `buffer_acc_loader_state`, `read_bpf_upgradeable_loader_state`, and `close_acc`. Nearby tests or test-like files include `src/flamenco/runtime/tests/test_exec_instr.c`, `src/flamenco/runtime/tests/run_native_tests.sh`.

## Before/After Behavior

Before the patch, after validating the buffer loader state and matching the stored buffer authority address to the provided authority account, the deploy path rejected only when `instr_acc_idxs[7] >= ctx.txn_ctx->txn_descriptor->signature_cnt`. After the patch, it rejects when `!fd_instr_acc_is_signer_idx(ctx.instr, 7)`, tying the authorization decision to the signer status of instruction account 7. The supplied authority-update, close, and cooldown hunks do not show meaningful behavioral changes beyond formatting in the provided evidence.

# Root Cause

The deploy path used an indirect transaction account index/signature-count comparison as the required-signature check instead of directly checking whether the authority instruction account was marked as a signer.

## Walkthrough

1. The deploy path reads the buffer account loader state and rejects non-buffer state.

2. It requires a non-null buffer authority address and compares that stored address to the provided authority account.

3. Before the fix, the required-signature gate used `instr_acc_idxs[7] >= ctx.txn_ctx->txn_descriptor->signature_cnt`.

4. After the fix, the gate uses `!fd_instr_acc_is_signer_idx(ctx.instr, 7)`.

5. This directly checks signer status for the instruction account used as the authority.

6. The provided evidence does not substantiate a separate close-path, redeployment-cooldown, memory-safety, or resource-exhaustion issue.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/flamenco/runtime/program/fd_bpf_loader_v3_program.c | 628 | Upgradeable BPF loader deploy path; reads buffer loader state, validates buffer authority, and enforces the required signer check before deployment-related state changes. |
| src/flamenco/runtime/program/fd_bpf_loader_v3_program.c | 1019 | Upgradeable loader authority update path; reads loader state and handles present/new authority accounts for buffer or loader-managed state. |
| src/flamenco/runtime/program/fd_bpf_loader_v3_program.c | 1078 | Upgradeable loader close path; reads loader state and borrows the close account for modification, but provided diff evidence here is formatting-only. |
| src/flamenco/runtime/program/fd_bpf_loader_v3_program.c | 1088 | Close/redeployment cooldown data-length handling; provided diff evidence is formatting-only around existing feature-gated resizing. |

## Code Snippets

## Snippet 1

Context: `src/flamenco/runtime/program/fd_bpf_loader_v3_program.c:628` (changes bounds, limits, or capacity handling)

Before
```c
fd_bpf_upgradeable_loader_state_t buffer_acc_loader_state;
    err = 0;
    if (!read_bpf_upgradeable_loader_state( &ctx, buffer_acc, &buffer_acc_loader_state, &err )) {
      FD_LOG_DEBUG(( "failed to read account metadata" ));
      return err;
    }
    if( !fd_bpf_upgradeable_loader_state_is_buffer( &buffer_acc_loader_state ) ) {
      return FD_EXECUTOR_INSTR_ERR_INVALID_ARG;
```
After
```c
fd_bpf_upgradeable_loader_state_t buffer_acc_loader_state;
    err = 0;
    if ( !read_bpf_upgradeable_loader_state( &ctx, buffer_acc, &buffer_acc_loader_state, &err ) ) {
      FD_LOG_DEBUG(( "failed to read account metadata" ));
      return err;
    }
    if ( !fd_bpf_upgradeable_loader_state_is_buffer( &buffer_acc_loader_state ) ) {
      return FD_EXECUTOR_INSTR_ERR_INVALID_ARG;
```

## Snippet 2

Context: `src/flamenco/runtime/program/fd_bpf_loader_v3_program.c:1019` (changes bounds, limits, or capacity handling)

Before
```c
fd_bpf_upgradeable_loader_state_t loader_state;
    int err = 0;
    if (!read_bpf_upgradeable_loader_state( &ctx, loader_acc, &loader_state, &err)) {
      // FIXME: HANDLE ERRORS!
      return err;
    }

    if( fd_bpf_upgradeable_loader_state_is_buffer( &loader_state ) ) {
```
After
```c
fd_bpf_upgradeable_loader_state_t loader_state;
    int err = 0;
    if ( !read_bpf_upgradeable_loader_state( &ctx, loader_acc, &loader_state, &err ) ) {
      // FIXME: HANDLE ERRORS!
      return err;
    }

    if ( fd_bpf_upgradeable_loader_state_is_buffer( &loader_state ) ) {
```

## Snippet 3

Context: `src/flamenco/runtime/program/fd_bpf_loader_v3_program.c:1078` (changes a sensitive control or state-update path)

Before
```c
fd_bpf_upgradeable_loader_state_t loader_state;
    int err = 0;
    if (!read_bpf_upgradeable_loader_state( &ctx, close_acc, &loader_state, &err ))
      return err;

    fd_borrowed_account_t * close_acc_rec = NULL;
    int write_result = fd_instr_borrowed_account_modify( &ctx, close_acc, 0UL, &close_acc_rec);
    if( FD_UNLIKELY( write_result != FD_ACC_MGR_SUCCESS ) ) {
```
After
```c
fd_bpf_upgradeable_loader_state_t loader_state;
    int err = 0;
    if ( !read_bpf_upgradeable_loader_state( &ctx, close_acc, &loader_state, &err ) )
      return err;

    fd_borrowed_account_t * close_acc_rec = NULL;
    int write_result = fd_instr_borrowed_account_modify( &ctx, close_acc, 0UL, &close_acc_rec );
    if( FD_UNLIKELY( write_result != FD_ACC_MGR_SUCCESS ) ) {
```

## Snippet 4

Context: `src/flamenco/runtime/program/fd_bpf_loader_v3_program.c:1088` (changes a sensitive control or state-update path)

Before
```c
}

    if (FD_FEATURE_ACTIVE(ctx.slot_ctx, enable_program_redeployment_cooldown)) {
      if (!fd_account_set_data_length2(&ctx, close_acc_rec->meta, close_acc, SIZE_OF_UNINITIALIZED, 0, &err)) {
        return err;
      }
```
After
```c
}

    if ( FD_FEATURE_ACTIVE( ctx.slot_ctx, enable_program_redeployment_cooldown ) ) {
      if ( !fd_account_set_data_length2( &ctx, close_acc_rec->meta, close_acc, SIZE_OF_UNINITIALIZED, 0, &err ) ) {
        return err;
      }
```

# Fix Pattern

Replace indirect authorization checks based on account ordering or signature-count metadata with direct signer-status checks for the specific instruction account that authorizes the state transition.

## How It Was Fixed

`fd_bpf_loader_v3_program_execute` now calls `fd_instr_acc_is_signer_idx(ctx.instr, 7)` for the deploy-path authority signer check. The existing buffer-state and authority-address checks remain in place. Test files were touched according to the commit metadata, but their contents are not provided.

# Why It Matters

1. Upgradeable loader deploy operations are privileged state transitions.

2. Authority address equality is not sufficient without signer verification.

3. A direct instruction signer check is stronger evidence of the intended authorization condition.

4. Formatting-only hunks should not be counted as independent security fixes.

# Evidence Notes

The strongest evidence is the semantic line change from `instr_acc_idxs[7] >= ctx.txn_ctx->txn_descriptor->signature_cnt` to `!fd_instr_acc_is_signer_idx(ctx.instr, 7)` in `src/flamenco/runtime/program/fd_bpf_loader_v3_program.c` around line 628. The commit subject names both a required signature check and an authorized program check, but the supplied hunks only support the required-signature portion. Nearby hunks around authority update, close, and redeployment cooldown are context or formatting-only in the provided evidence. Protocol security invariant: Upgradeable BPF loader deployment must require the relevant authority instruction account to be marked as a signer before loader-managed program state can be changed. Verification notes: The patch evidence proves an authorization check was corrected, but does not by itself prove a complete exploit path. The evidence does not show whether unauthorized deployment was practically reachable in all transaction/account layouts. The close-account and redeployment-cooldown hunks shown are not independently security-relevant; they appear formatting-only in the provided context. The provided evidence does not substantiate a memory-safety bug or resource-exhaustion vulnerability. The authorized program check named in the subject is not fully visible in the supplied hunks, so details of that part should not be overclaimed. Confirmed semantic authorization change in the deploy path from the supplied diff. No complete exploit path is proven by the provided evidence. No independent vulnerability is supported for the close or cooldown hunks. Test coverage was mentioned in metadata but not available for content review. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final confidence: `medium`

The supplied evidence supports retaining this as a security fix: the deploy path in the upgradeable BPF loader changed from an indirect signature-count/account-index gate to a direct signer-status check for instruction account 7. That is a concrete authorization check correction in a privileged blockchain program deployment path. However, the evidence does not prove a complete exploit path or substantiate the separate authorized-program-check claim, so the original high confidence should be reduced.

## Security Evidence

1. Commit subject explicitly says it fixes a required signature check.
2. Patch replaces `instr_acc_idxs[7] >= ctx.txn_ctx->txn_descriptor->signature_cnt` with `!fd_instr_acc_is_signer_idx(ctx.instr, 7)`.
3. Changed code is in the upgradeable BPF loader deploy path, a privileged state-transition path.
4. The corrected check directly verifies signer status for the authority instruction account.

## Missing Evidence

1. No full exploit scenario is provided showing unauthorized deployment in practice.
2. Test contents are not provided, only test file metadata.
3. The supplied hunks do not substantiate the separate authorized program check named in the commit subject.
4. Other shown hunks around authority update, close, and cooldown appear formatting-only from the provided evidence.

## Claim Boundaries

1. Keep the corpus entry focused on the required-signature authorization check in the deploy path.
2. Do not claim memory-safety, resource-exhaustion, close-path, or cooldown vulnerabilities from this evidence.
3. Do not claim the authorized-program-check fix unless additional patch evidence is supplied.
4. Impact should be framed as potential privilege misuse through an incorrect signer/authorization check, not as a proven end-to-end exploit.
