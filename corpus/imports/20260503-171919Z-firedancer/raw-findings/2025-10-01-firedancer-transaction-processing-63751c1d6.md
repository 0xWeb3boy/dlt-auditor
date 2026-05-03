---
case_id: case_20251001_63751c1d6
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-10-01
source_refs:
  - git:63751c1d608593fecae2b6fe08c9523aff7be356
  - "src/discof/resolv/fd_resolv_tile.c:254"
  - "src/disco/metrics/generated/fd_metrics_resolf.h:17"
  - "src/disco/metrics/generated/fd_metrics_resolf.h:4"
  - "src/discof/resolv/fd_resolv_tile.c:487"
bug_class: race-condition
impact_type:
  - state-consistency
  - correctness-or-hardening
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - replay
  - address-lookup-tables
  - toctou
  - state-consistency
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Firedancer's resolv ALUT path to drop/count transactions when `ctx->bank` is unavailable and to pass a slot-derived `fd_funk_txn_xid_t` to address lookup table loading instead of using `NULL` for the root Funk transaction. The removed TODO explicitly mentions TOCTOU issues from replay swapping the Funk root, so the change may be security relevant, but the supplied evidence does not establish an exploitable vulnerability or concrete protocol failure.

## Observed Patch Facts

1. In `src/discof/resolv/fd_resolv_tile.c`, the patch replaces `FD_TEST( sysvar_cache );` with `if( FD_UNLIKELY( !ctx->bank ) ) {`.

2. In `src/disco/metrics/generated/fd_metrics_resolf.h`, the patch replaces `#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_INSERTED_OFF (16UL)` with `#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_INSERTED_OFF (17UL)`.

3. In `src/disco/metrics/generated/fd_metrics_resolf.h`, the patch replaces `#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_OFF (16UL)` with `#define FD_METRICS_COUNTER_RESOLF_NO_BANK_DROP_OFF (16UL)`.

4. In `src/discof/resolv/fd_resolv_tile.c`, the patch replaces `/* TODO: As above, should probably try and use a funk transaction` with `fd_funk_txn_xid_t xid = { .ul = { fd_bank_slot_get( ctx->bank ), fd_bank_slot_get( ct...`.

## Project Context

The changed code sits primarily in `src/discof/resolv`, `src/discof`, `src/disco/metrics/generated`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/disco/metrics/generated/fd_metrics_bank.h`, `src/disco/metrics/generated/fd_metrics_replay.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/disco/metrics/generated/fd_metrics_replay.h`, `src/discof/rpcserver/fd_rpc_service.c`. The strongest project-level identifiers around this patch are `define`, `bank`, `root`, and `transaction`. Nearby tests or test-like files include `src/discof/backtest/fd_backtest_tile.c`, `src/discof/backtest/fd_backtest_rocksdb.h`.

## Before/After Behavior

Before the patch, ALUT handling could query `fd_bank_sysvar_cache_query(ctx->bank)` without an explicit missing-bank guard, and one ALUT load path passed `NULL` to `fd_runtime_load_txn_address_lookup_tables`, documented as using the root Funk transaction. After the patch, missing bank causes a counted drop via `RESOLF_NO_BANK_DROP`, and ALUT loading uses an xid built from `fd_bank_slot_get(ctx->bank)`. Generated metrics were updated to add the new no-bank drop counter and shift later offsets.

# Root Cause

The resolver ALUT code used bank-dependent state without first guarding one missing-bank path and used the mutable root Funk transaction view for ALUT loading. The code comment supports a TOCTOU state-consistency concern, but not a proven security vulnerability.

## Walkthrough

1. A transaction with `txnt->addr_table_adtl_cnt` enters the resolver address lookup table path.

2. Previously, `publish_txn` queried sysvar cache through `ctx->bank` before explicitly checking that `ctx->bank` existed.

3. Previously, another ALUT load path passed `NULL` as the Funk transaction argument, meaning the root Funk transaction was used.

4. The removed comment stated that using the root in this way had TOCTOU issues because replay could swap the Funk root in the background.

5. The patch drops and counts ALUT transactions when no bank is available.

6. The patch constructs a slot-derived `fd_funk_txn_xid_t` and passes it to ALUT loading instead of `NULL`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/discof/resolv/fd_resolv_tile.c | 254 | publishing stashed transactions with address lookup tables; now requires an available bank before sysvar and ALUT resolution |
| src/discof/resolv/fd_resolv_tile.c | 487 | fragment handling path loading transaction address lookup tables against a slot-specific Funk transaction xid instead of NULL root |
| src/disco/metrics/generated/fd_metrics_resolf.h | 4 | generated observability counter for transactions dropped because bank was unavailable |

## Code Snippets

## Snippet 1

Context: `src/discof/resolv/fd_resolv_tile.c:254` (changes signature or replay validation logic)

Before
```c
if( FD_UNLIKELY( txnt->addr_table_adtl_cnt ) ) {
    fd_sysvar_cache_t const * sysvar_cache = fd_bank_sysvar_cache_query( ctx->bank );
    FD_TEST( sysvar_cache );

    /* TODO: We really should use a specific transaction for the root
       slot, not "NULL" which has TOCTOU issues with replay swapping
       the funk root in the background.  If we took any reference to
```
After
```c
if( FD_UNLIKELY( txnt->addr_table_adtl_cnt ) ) {
    if( FD_UNLIKELY( !ctx->bank ) ) {
      FD_MCNT_INC( RESOLF, NO_BANK_DROP, 1 );
      return 0;
    }

    fd_sysvar_cache_t const * sysvar_cache = fd_bank_sysvar_cache_query( ctx->bank );
```

## Snippet 2

Context: `src/disco/metrics/generated/fd_metrics_resolf.h:17` (changes a sensitive control or state-update path)

Before
```c
#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_CNT  (4UL)

#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_INSERTED_OFF (16UL)
#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_OVERRUN_OFF (17UL)
#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_PUBLISHED_OFF (18UL)
#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_REMOVED_OFF (19UL)

#define FD_METRICS_COUNTER_RESOLF_LUT_RESOLVED_OFF  (20UL)
```
After
```c
#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_CNT  (4UL)

#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_INSERTED_OFF (17UL)
#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_OVERRUN_OFF (18UL)
#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_PUBLISHED_OFF (19UL)
#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_REMOVED_OFF (20UL)

#define FD_METRICS_COUNTER_RESOLF_LUT_RESOLVED_OFF  (21UL)
```

## Snippet 3

Context: `src/disco/metrics/generated/fd_metrics_resolf.h:4` (changes a sensitive control or state-update path)

Before
```c
#include "fd_metrics_enums.h"

#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_OFF  (16UL)
#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_NAME "resolf_stash_operation"
#define FD_METRICS_COUNTER_RESOLF_STASH_OPERATION_TYPE (FD_METRICS_TYPE_COUNTER)
```
After
```c
#include "fd_metrics_enums.h"

#define FD_METRICS_COUNTER_RESOLF_NO_BANK_DROP_OFF  (16UL)
#define FD_METRICS_COUNTER_RESOLF_NO_BANK_DROP_NAME "resolf_no_bank_drop"
#define FD_METRICS_COUNTER_RESOLF_NO_BANK_DROP_TYPE (FD_METRICS_TYPE_COUNTER)
#define FD_METRICS_COUNTER_RESOLF_NO_BANK_DROP_DESC "Count of transactions dropped because the bank was not available"
#define FD_METRICS_COUNTER_RESOLF_NO_BANK_DROP_CVT  (FD_METRICS_CONVERTER_NONE)
```

## Snippet 4

Context: `src/discof/resolv/fd_resolv_tile.c:487` (changes a sensitive control or state-update path)

Before
```c
FD_TEST( slot_hashes );

    /* TODO: As above, should probably try and use a funk transaction
       referencing the specific root slot. */
    int result = fd_runtime_load_txn_address_lookup_tables( txnt,
                                                            fd_txn_m_payload( txnm ),
                                                            ctx->funk,
                                                            NULL, /* NULL is the root Funk transaction */
```
After
```c
FD_TEST( slot_hashes );

    fd_funk_txn_xid_t xid = { .ul = { fd_bank_slot_get( ctx->bank ), fd_bank_slot_get( ctx->bank ) } };

    int result = fd_runtime_load_txn_address_lookup_tables( txnt,
                                                            fd_txn_m_payload( txnm ),
                                                            ctx->funk,
                                                            &xid,
```

# Fix Pattern

Add an explicit prerequisite-state guard before bank-dependent lookup work and bind lookup state to a slot-derived transaction identifier instead of a mutable root view.

## How It Was Fixed

`src/discof/resolv/fd_resolv_tile.c` now checks `!ctx->bank` before sysvar cache access in the stashed transaction publish path, increments `RESOLF_NO_BANK_DROP`, and returns. The ALUT loading path now constructs `fd_funk_txn_xid_t xid = { .ul = { fd_bank_slot_get(ctx->bank), fd_bank_slot_get(ctx->bank) } }` and passes `&xid` to `fd_runtime_load_txn_address_lookup_tables`. Generated resolf metric definitions add the corresponding no-bank drop counter.

# Why It Matters

1. Avoids continuing ALUT lookup work without required bank state.

2. Avoids relying on a root Funk view that the removed comment describes as TOCTOU-prone.

3. Improves observability for missing-bank drops.

4. Security impact is plausible but not demonstrated by the provided evidence.

# Evidence Notes

Grounded evidence is limited to the resolver code changes and generated metrics updates. The strongest support is the removed TODO explicitly identifying TOCTOU issues with `NULL` root Funk transaction use. The evidence does not show attacker control, remote triggerability, consensus divergence, funds impact, or a concrete denial-of-service condition. Metrics files are support instrumentation, not root-cause security fixes. Protocol security invariant: Transactions that use address lookup tables should be resolved against a bank and Funk transaction view matching the intended slot; if no bank is available, resolver logic should not continue into bank-dependent lookup work. Verification notes: The patch does not prove a remotely exploitable vulnerability. The patch does not prove consensus divergence occurred in production. The patch does not show attacker control over replay root swapping timing. The metrics offset changes are instrumentation/baseline updates, not security fixes by themselves. The null-bank guard may also prevent crashes or operational failures, but denial-of-service impact is not proven from the provided evidence. No exploit path is established by the supplied input. No production incident or consensus failure is shown. No tests or issue discussion are provided. Generated metrics changes should be treated as observability support only. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `race-condition`
Final impact type: `state-consistency, correctness-or-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, replay, address-lookup-tables, toctou, state-consistency`

The supplied patch evidence supports retaining this as security hardening, not a proven security fix. The strongest signal is that resolver ALUT loading stopped using the mutable root Funk transaction and now binds lookup state to a slot-derived transaction xid, with the removed comment explicitly describing TOCTOU issues from replay swapping the Funk root. The added missing-bank drop also avoids continuing bank-dependent lookup work without required state. However, the evidence does not prove attacker control, exploitability, consensus divergence, or a concrete denial-of-service condition.

## Security Evidence

1. ALUT resolution is in a blockchain transaction-processing path tied to bank, slot, replay, and Funk state.
2. Patch replaces NULL root Funk transaction use with a slot-derived fd_funk_txn_xid_t passed to fd_runtime_load_txn_address_lookup_tables.
3. Removed comment explicitly identifies TOCTOU issues with replay swapping the Funk root in the background.
4. Patch adds an explicit !ctx->bank guard before bank-dependent sysvar cache and ALUT work, dropping and counting affected transactions.

## Missing Evidence

1. No advisory, issue discussion, or commit body states a security vulnerability.
2. No exploit path or attacker-controlled timing is shown.
3. No evidence of consensus divergence, funds impact, or production incident is provided.
4. No tests or failure reproduction demonstrate a concrete security impact.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix.
2. Do not claim proven remote exploitability or attacker-triggered DoS.
3. Do not treat generated metrics offset changes as security fixes by themselves.
4. Do not preserve the original input-validation bug class; the supported issue is replay/state consistency and TOCTOU hardening.
