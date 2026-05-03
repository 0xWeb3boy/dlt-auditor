---
case_id: case_20250110_63a0855e2
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2025-01-10
source_refs:
  - git:63a0855e226a3753f4dc188aa059a95b418f59a2
  - "src/flamenco/runtime/program/fd_system_program_nonce.c:1064"
  - "src/flamenco/runtime/context/fd_exec_txn_ctx.h:91"
  - "src/flamenco/runtime/fd_runtime.c:1443"
  - "src/flamenco/runtime/fd_runtime.c:1867"
bug_class: nonce-state-persistence
impact_type:
  - replay-protection
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - consensus
  - durable-nonce
  - replay-protection
  - state-persistence
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Firedancer runtime nonce handling so an authorized durable nonce account is explicitly tracked and finalized. Instead of returning success immediately after nonce authority validation, the code records the nonce account index, prepares the account state to persist if execution fails, and updates both finalization paths to save either the advanced nonce account or that prepared failure-state account. The evidence supports a likely replay-sensitive nonce state persistence fix, but not a concrete exploit, funds theft, or demonstrated consensus split.

## Observed Patch Facts

1. In `src/flamenco/runtime/program/fd_system_program_nonce.c`, the patch replaces `return FD_RUNTIME_EXECUTE_SUCCESS;` with `/*`.

2. In `src/flamenco/runtime/context/fd_exec_txn_ctx.h`, the patch replaces `uchar nonce_accounts[ MAX_TX_ACCOUNT_LOCKS ]; /* Nonce accounts in the txn to be save...` with `/* This is a bit of a misnomer but Agave calls it "rollback".`.

3. In `src/flamenco/runtime/fd_runtime.c`, the patch replaces `for( ulong i=1UL; i<txn_ctx->accounts_cnt; i++ ) {` with `if( txn_ctx->nonce_account_idx_in_txn != ULONG_MAX ) {`.

4. In `src/flamenco/runtime/fd_runtime.c`, the patch replaces `for( ulong i=1UL; i<txn_ctx->accounts_cnt; i++ ) {` with `if( txn_ctx->nonce_account_idx_in_txn != ULONG_MAX ) {`.

## Project Context

The changed code sits primarily in `src/flamenco/runtime/program`, `src/flamenco/runtime`, `src/flamenco/runtime/context`, which anchors the finding in the `consensus` area of the project. Historical context from `src/flamenco/runtime/fd_executor.c`, `src/flamenco/runtime/fd_account.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/flamenco/runtime/fd_executor.c`, `src/flamenco/runtime/fd_runtime.h`. The strongest project-level identifiers around this patch are `txn_ctx`, `queue`, `slot_ctx`, and `account`. Nearby tests or test-like files include `src/flamenco/runtime/tests/fd_exec_instr_test.c`, `src/flamenco/runtime/tests/fd_dump_pb.c`.

## Before/After Behavior

Before the patch, the authorized nonce path in `fd_check_transaction_age` could return success without recording the nonce account in explicit transaction context state. Finalization later rediscovered nonce accounts through marker-array logic and conditionally saved them based on blockhash validity. After the patch, authorization records `nonce_account_idx_in_txn`, prepares `rollback_nonce_account[0]`, tracks whether the nonce was advanced, and finalization saves the correct nonce account record in both single-threaded and thread-pool paths.

# Root Cause

Nonce authorization and nonce account persistence were not tied together strongly enough in transaction context. The pre-patch path could accept an authorized durable nonce transaction without preparing or carrying the nonce account state that finalization must persist if execution later fails.

## Walkthrough

1. A durable nonce transaction reaches `fd_check_transaction_age`.

2. The nonce authority check finds a signer matching the initialized nonce authority.

3. Before the patch, that path returned `FD_RUNTIME_EXECUTE_SUCCESS` immediately.

4. After the patch, the same path records `instr_accts[0]` in `txn_ctx->nonce_account_idx_in_txn`.

5. The patched code initializes `txn_ctx->rollback_nonce_account[0]` and views the nonce account to prepare the failed-execution state.

6. The transaction context replaces the old nonce marker array with explicit nonce account index, advanced flag, and rollback/failure-state storage.

7. Single-thread finalization now saves the tracked nonce account if one exists.

8. If the nonce was already advanced, finalization saves the borrowed nonce account; otherwise it saves `rollback_nonce_account[0]`.

9. The thread-pool finalization path applies the same selection logic when building `accounts_to_save`.

10. This makes nonce account persistence an explicit part of transaction finalization.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/flamenco/runtime/program/fd_system_program_nonce.c | 1064 | Nonce authorization path now marks the transaction nonce account and prepares the state that should be persisted if execution later fails. |
| src/flamenco/runtime/context/fd_exec_txn_ctx.h | 91 | Transaction context now stores a single tracked nonce account index, an advanced flag, and the rollback/failed-transaction nonce account state. |
| src/flamenco/runtime/fd_runtime.c | 1443 | Single-thread transaction finalization saves the advanced nonce account or the prepared failure-state nonce account. |
| src/flamenco/runtime/fd_runtime.c | 1867 | Thread-pool transaction finalization adds the same nonce-account save behavior to the batched save list. |

## Code Snippets

## Snippet 1

Context: `src/flamenco/runtime/program/fd_system_program_nonce.c:1064` (changes signature or replay validation logic)

Before
```c
if( fd_txn_is_signer( txn_ctx->txn_descriptor, (int)instr_accts[i] ) ) {
      if( !memcmp( &txn_ctx->accounts[ instr_accts[i] ], &state.inner.current.inner.initialized.authority, sizeof( fd_pubkey_t ) ) ) {
        return FD_RUNTIME_EXECUTE_SUCCESS;
      }
```
After
```c
if( fd_txn_is_signer( txn_ctx->txn_descriptor, (int)instr_accts[i] ) ) {
      if( !memcmp( &txn_ctx->accounts[ instr_accts[i] ], &state.inner.current.inner.initialized.authority, sizeof( fd_pubkey_t ) ) ) {
        /*
           Mark nonce account to make sure that we modify and hash the
           account even if the transaction failed to execute
           successfully.
         */
        txn_ctx->nonce_account_idx_in_txn = instr_accts[ 0 ];
```

## Snippet 2

Context: `src/flamenco/runtime/context/fd_exec_txn_ctx.h:91` (changes signature or replay validation logic)

Before
```c
fd_borrowed_account_t executable_accounts[ MAX_TX_ACCOUNT_LOCKS ]; /* Array of BPF upgradeable loader program data accounts */
  fd_borrowed_account_t borrowed_accounts[ MAX_TX_ACCOUNT_LOCKS ];   /* Array of borrowed accounts accessed by this transaction. */
  uchar                 nonce_accounts[ MAX_TX_ACCOUNT_LOCKS ];      /* Nonce accounts in the txn to be saved */
  uint                  num_instructions;                            /* Counter for number of instructions in txn */
  fd_txn_return_data_t  return_data;                                 /* Data returned from `return_data` syscalls */
```
After
```c
fd_borrowed_account_t executable_accounts[ MAX_TX_ACCOUNT_LOCKS ]; /* Array of BPF upgradeable loader program data accounts */
  fd_borrowed_account_t borrowed_accounts[ MAX_TX_ACCOUNT_LOCKS ];   /* Array of borrowed accounts accessed by this transaction. */
  /* This is a bit of a misnomer but Agave calls it "rollback".
     This is the account state that the nonce account should be in when
     the txn fails.
     It will advance the nonce account, rather than "roll back".
   */
  fd_borrowed_account_t rollback_nonce_account[ 1 ];
```

## Snippet 3

Context: `src/flamenco/runtime/fd_runtime.c:1443` (changes bounds, limits, or capacity handling)

Before
```c
fd_acc_mgr_save_non_tpool( slot_ctx->acc_mgr, slot_ctx->funk_txn, &txn_ctx->borrowed_accounts[0] );

    for( ulong i=1UL; i<txn_ctx->accounts_cnt; i++ ) {
      if( txn_ctx->nonce_accounts[i] ) {
        ushort                recent_blockhash_off = txn_ctx->txn_descriptor->recent_blockhash_off;
        fd_hash_t *           recent_blockhash     = (fd_hash_t *)((uchar *)txn_ctx->_txn_raw->raw + recent_blockhash_off);
        fd_block_hash_queue_t queue                = slot_ctx->slot_bank.block_hash_queue;
        ulong                 queue_sz             = fd_hash_hash_age_pair_t_map_size( queue.ages_pool, queue.ages_root );
```
After
```c
fd_acc_mgr_save_non_tpool( slot_ctx->acc_mgr, slot_ctx->funk_txn, &txn_ctx->borrowed_accounts[0] );

    if( txn_ctx->nonce_account_idx_in_txn != ULONG_MAX ) {
      if( FD_LIKELY( txn_ctx->nonce_account_advanced ) ) {
        fd_acc_mgr_save_non_tpool( slot_ctx->acc_mgr, slot_ctx->funk_txn, &txn_ctx->borrowed_accounts[ txn_ctx->nonce_account_idx_in_txn ] );
      } else {
        fd_acc_mgr_save_non_tpool( slot_ctx->acc_mgr, slot_ctx->funk_txn, &txn_ctx->rollback_nonce_account[ 0 ] );
      }
```

## Snippet 4

Context: `src/flamenco/runtime/fd_runtime.c:1867` (changes bounds, limits, or capacity handling)

Before
```c
accounts_to_save[acc_idx++] = &txn_ctx->borrowed_accounts[ FD_FEE_PAYER_TXN_IDX ];
        for( ulong i=1UL; i<txn_ctx->accounts_cnt; i++ ) {
          if( txn_ctx->nonce_accounts[i] ) {
            ushort                recent_blockhash_off = txn_ctx->txn_descriptor->recent_blockhash_off;
            fd_hash_t *           recent_blockhash     = (fd_hash_t *)((uchar *)txn_ctx->_txn_raw->raw + recent_blockhash_off);
            fd_block_hash_queue_t queue                = slot_ctx->slot_bank.block_hash_queue;
            ulong                 queue_sz             = fd_hash_hash_age_pair_t_map_size( queue.ages_pool, queue.ages_root );
```
After
```c
accounts_to_save[acc_idx++] = &txn_ctx->borrowed_accounts[ FD_FEE_PAYER_TXN_IDX ];
        if( txn_ctx->nonce_account_idx_in_txn != ULONG_MAX ) {
          if( FD_LIKELY( txn_ctx->nonce_account_advanced ) ) {
            accounts_to_save[acc_idx++] = &txn_ctx->borrowed_accounts[ txn_ctx->nonce_account_idx_in_txn ];
          } else {
            accounts_to_save[acc_idx++] = &txn_ctx->rollback_nonce_account[ 0 ];
          }
```

# Fix Pattern

Record replay-sensitive nonce state at authorization time and pass explicit transaction-context state into all finalization paths, instead of rediscovering nonce accounts later through marker arrays and blockhash checks.

## How It Was Fixed

The patch adds transaction context fields for the nonce account index, whether the nonce was advanced, and a prepared failure-state account record. It updates nonce authorization to populate those fields, then updates both transaction finalization implementations to persist the selected nonce account record.

# Why It Matters

1. Durable nonce account state is replay-sensitive.

2. Failed execution still needs deterministic nonce account finalization.

3. Single-thread and thread-pool finalization must agree.

4. The patch affects account saving and hashing behavior.

5. The evidence does not establish a specific attacker workflow.

# Evidence Notes

Grounded evidence comes from `fd_system_program_nonce.c`, where authorized nonce handling now records `nonce_account_idx_in_txn` and prepares rollback/failure-state account data; `fd_exec_txn_ctx.h`, where explicit nonce tracking fields are added; and `fd_runtime.c`, where both finalization paths now save the tracked nonce account. Claims about concrete exploitation, theft, privilege escalation, or an observed consensus split are unsupported by the provided input. Protocol security invariant: An authorized durable nonce transaction must cause the nonce account state selected for finalization to be persisted, including when later execution fails, so nonce consumption is reflected in account state and hashing. Verification notes: The patch does not prove a specific exploit transaction or attacker workflow. The patch does not prove funds theft, privilege escalation, or consensus split by itself. The exact pre-patch failure condition is inferred from changed persistence behavior, not demonstrated by a test trace in the provided input. This should not be classified as a cryptographic primitive flaw; it is nonce account state handling in the runtime. Classified as likely security because the changed logic is nonce/account persistence in a replay-sensitive runtime path. Confidence downgraded to medium because the provided evidence does not include a failing test, exploit trace, or protocol citation proving exploitability. Kept in the security corpus as a likely security fix, bounded to durable nonce state persistence rather than cryptography or authorization bypass. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `nonce-state-persistence`
Final impact type: `replay-protection, state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, durable-nonce, replay-protection, state-persistence`

The supplied patch evidence supports retaining this as security hardening, not a confidently proven security fix. The code explicitly changes durable nonce transaction handling so the nonce account is tracked, modified, hashed, and saved even when later transaction execution fails. That is security-sensitive because durable nonce state is replay-protection state in a blockchain runtime. However, the provided evidence does not include an exploit trace, failing regression, consensus divergence proof, or protocol citation showing a concrete vulnerability was reachable.

## Security Evidence

1. Nonce authorization no longer returns immediately; it records the nonce account index for later finalization.
2. The new comment says the nonce account must be modified and hashed even if transaction execution fails.
3. Transaction context now stores rollback/failure-state nonce account data and an advanced flag.
4. Both finalization paths save either the advanced nonce account or the prepared failure-state account.
5. The affected code is in runtime transaction execution/finalization for durable nonce account state.

## Missing Evidence

1. No concrete attacker workflow or replay transaction is shown.
2. No failing test output or regression case is provided in the input.
3. No proof is provided that the old behavior caused accepted replay, consensus split, or funds loss.
4. No protocol reference is supplied proving the exact required failed-transaction nonce semantics.

## Claim Boundaries

1. Classify as durable nonce state persistence hardening, not a cryptographic primitive flaw.
2. Do not claim theft, privilege escalation, or demonstrated consensus failure from this evidence alone.
3. Do not rely on the removed blockhash queue logic as a resource-control security issue.
4. The evidence supports replay-sensitive state-integrity risk, but exploitability remains unproven.
