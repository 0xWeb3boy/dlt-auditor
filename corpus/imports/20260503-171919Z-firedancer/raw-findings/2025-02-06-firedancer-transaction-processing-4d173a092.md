---
case_id: case_20250206_4d173a092
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-02-06
source_refs:
  - git:4d173a0927af12fc840bd4755530eb1bb845058a
  - "src/disco/pack/fd_pack_cost.h:197"
  - "src/disco/pack/fd_pack_cost.h:4"
  - "src/app/fdctl/run/tiles/fd_bank.c:247"
  - "src/app/fdctl/run/tiles/fd_bank.c:207"
bug_class: resource-accounting-mismatch
impact_type:
  - consensus-resource-accounting
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - resource-accounting
  - cost-model
  - validator
  - consensus
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes Firedancer pack and bank compute-cost accounting by making loaded accounts data cost explicit and by separating execution CUs from account-data CUs in bank-side consumed-cost handling. This is plausibly consensus-sensitive resource-accounting work because the surrounding pack constants are marked consensus critical, but the provided evidence does not prove exploitability, invalid transaction execution, a consensus split, or a concrete adversarial scenario.

## Observed Patch Facts

1. In `src/disco/pack/fd_pack_cost.h`, the patch replaces `ulong * opt_precompile_sig_cnt ) {` with `ulong * opt_precompile_sig_cnt,`.

2. In `src/disco/pack/fd_pack_cost.h`, the patch replaces `* per-signature cost` with `* per-signature cost: The costs associated with transaction`.

3. In `src/app/fdctl/run/tiles/fd_bank.c`, the patch replaces `uint executed_cus = consumed_cus[ sanitized_idx-1UL ];` with `uint actual_execution_cus = consumed_exec_cus[ sanitized_idx-1UL ];`.

4. In `src/app/fdctl/run/tiles/fd_bank.c`, the patch replaces `uint requested_cus = txn->pack_cu.requested_execution_cus;` with `uint requested_exec_plus_acct_data_cus = txn->pack_cu.requested_exec_plus_acct_data_cus;`.

## Project Context

The changed code sits primarily in `src/disco/pack`, `src/disco`, `src/app/fdctl/run/tiles`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/disco/pack/fd_pack.h`, `src/disco/pack/fd_pack.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/disco/pack/fd_pack.h`, `src/disco/pack/fd_pack.c`. The strongest project-level identifiers around this patch are `cost`, `non_execution_cus`, `ulong`, and `model`. Nearby tests or test-like files include `src/disco/pack/fuzz_compute_budget_program_parse.c`, `src/disco/rpcserver/fuzz_json_lex.c`.

## Before/After Behavior

Before the patch, `fd_pack_compute_cost` exposed execution cost, fee, and precompile signature count outputs, but the shown signature did not expose loaded accounts data cost separately. Bank-side code used a single consumed-CU value as executed CUs and computed actual consumption as non-execution plus that value. After the patch, loaded accounts data cost is a separate output, bank-side execution results are split into execution CUs and account-data CUs, actual consumption sums non-execution, execution, and account-data costs, and simple vote transactions explicitly receive fixed execution cost with zero account-data cost.

# Root Cause

The supported root cause is inconsistent or incomplete resource accounting between pack cost calculation and bank execution accounting. The evidence supports a cost-model mismatch, not a signature-validation, replay, authorization, or direct transaction-validity bug.

## Walkthrough

1. `fd_pack_compute_cost` in `src/disco/pack/fd_pack_cost.h` gains an `opt_loaded_accounts_data_cost` output parameter.

2. Cost-model comments are expanded to describe transaction signature and precompile signature costs more precisely.

3. `fd_bank.c` changes from reading one `consumed_cus` value to using separate `consumed_exec_cus` and `consumed_acct_data_cus` values.

4. Actual consumed CUs are computed as non-execution CUs plus actual execution CUs plus actual account-data CUs.

5. Simple vote transactions receive explicit fixed-cost handling, setting execution cost to `FD_PACK_VOTE_DEFAULT_COMPUTE_UNITS` and account-data cost to zero.

6. The surrounding pack constants are marked consensus critical, but the evidence does not show a concrete vulnerability trigger or impact.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/disco/pack/fd_pack_cost.h | 191 | Computes per-transaction pack cost and now exposes loaded accounts data cost as a distinct cost component. |
| src/disco/pack/fd_pack_cost.h | 1 | Documents the transaction cost model components, including precompile signatures and loaded account data. |
| src/app/fdctl/run/tiles/fd_bank.c | 201 | Receives bank execution results and separates requested execution plus account-data CUs from non-execution CUs, with special handling for simple votes. |
| src/app/fdctl/run/tiles/fd_bank.c | 241 | Computes actual consumed CUs from non-execution, execution, and account-data costs after transaction execution. |
| src/disco/pack/fd_pack.h | 13 | Defines consensus-critical block and vote cost limits that the packer must respect. |

## Code Snippets

## Snippet 1

Context: `src/disco/pack/fd_pack_cost.h:197` (changes signature or replay validation logic)

Before
```c
ulong          * opt_execution_cost,
                      ulong          * opt_fee,
                      ulong          * opt_precompile_sig_cnt ) {

#define ROW(x) fd_pack_builtin_tbl + MAP_PERFECT_HASH_PP( x )

  fd_pack_builtin_prog_cost_t const * compute_budget_row     = ROW( COMPUTE_BUDGET_PROG_ID );
  fd_pack_builtin_prog_cost_t const * vote_row               = ROW( VOTE_PROG_ID           );
```
After
```c
ulong          * opt_execution_cost,
                      ulong          * opt_fee,
                      ulong          * opt_precompile_sig_cnt,
                      ulong          * opt_loaded_accounts_data_cost ) {

#define ROW(x) fd_pack_builtin_tbl + MAP_PERFECT_HASH_PP( x )
  fd_pack_builtin_prog_cost_t const * compute_budget_row     = ROW( COMPUTE_BUDGET_PROG_ID );
  fd_pack_builtin_prog_cost_t const * ed25519_precompile_row = ROW( ED25519_SV_PROG_ID     );
```

## Snippet 2

Context: `src/disco/pack/fd_pack_cost.h:4` (changes signature or replay validation logic)

Before
```c
#include "fd_compute_budget_program.h"
#include "../../flamenco/runtime/fd_system_ids_pp.h"

/* The functions in this header implement the transaction cost model
   that is soon to be part of consensus.
   The cost model consists of several components:
     * per-signature cost
     * per-write-lock cost
```
After
```c
#include "fd_compute_budget_program.h"
#include "../../flamenco/runtime/fd_system_ids_pp.h"
#include "../../ballet/txn/fd_txn.h"

/* The functions in this header implement the transaction cost model
   that is soon to be part of consensus.
   The cost model consists of several components:
     * per-signature cost: The costs associated with transaction
```

## Snippet 3

Context: `src/app/fdctl/run/tiles/fd_bank.c:247` (changes a sensitive control or state-update path)

Before
```c
else                                       ctx->metrics.success++;

    uint executed_cus                = consumed_cus[ sanitized_idx-1UL ];
    txn->bank_cu.actual_consumed_cus = non_execution_cus + executed_cus;
    if( FD_UNLIKELY( executed_cus>requested_cus ) ) {
      /* There's basically a bug in the Agave codebase right now
         regarding the cost model for some transactions.  Some built-in
         instructions like creating an address lookup table consume more
```
After
```c
else                                       ctx->metrics.success++;

    uint actual_execution_cus        = consumed_exec_cus[ sanitized_idx-1UL ];
    uint actual_acct_data_cus        = consumed_acct_data_cus[ sanitized_idx-1UL ];
    txn->bank_cu.actual_consumed_cus = non_execution_cus + actual_execution_cus + actual_acct_data_cus;

    /* The VM will stop executing and fail an instruction immediately if
       it exceeds its requested CUs.  A transaction which requests less
```

## Snippet 4

Context: `src/app/fdctl/run/tiles/fd_bank.c:207` (changes a sensitive control or state-update path)

Before
```c
fd_txn_p_t * txn = (fd_txn_p_t *)( dst + (i*sizeof(fd_txn_p_t)) );

    uint requested_cus       = txn->pack_cu.requested_execution_cus;
    uint non_execution_cus   = txn->pack_cu.non_execution_cus;
    /* Assume failure, set below if success.  If it doesn't land in the
       block, rebate the non-execution CUs too. */
    txn->bank_cu.rebated_cus = requested_cus + non_execution_cus;
    txn->flags               &= ~FD_TXN_P_FLAGS_EXECUTE_SUCCESS;
```
After
```c
fd_txn_p_t * txn = (fd_txn_p_t *)( dst + (i*sizeof(fd_txn_p_t)) );

    uint requested_exec_plus_acct_data_cus = txn->pack_cu.requested_exec_plus_acct_data_cus;
    uint non_execution_cus       = txn->pack_cu.non_execution_cus;

    if( FD_UNLIKELY( fd_txn_is_simple_vote_transaction( TXN(txn), txn->payload ) ) ) {
      /* Simple votes are charged fixed amounts of compute regardless of
      the real cost they incur.  fd_ext_bank_load_and_execute_txns
```

# Fix Pattern

Represent distinct resource-cost components explicitly and keep pack-side cost calculation aligned with bank-side execution accounting.

## How It Was Fixed

The patch adds loaded accounts data cost as an explicit output from the pack cost calculation, updates documentation around modeled cost components, splits bank-side consumed compute into execution and account-data components, sums both into actual consumed CUs, and preserves fixed simple-vote cost semantics explicitly.

# Why It Matters

1. Cost-model mismatches can affect transaction packing decisions.

2. The touched pack limits are described as consensus critical in the provided context.

3. Loaded accounts data cost is now accounted for separately.

4. The evidence does not prove an exploitable vulnerability.

# Evidence Notes

Grounded evidence comes from `src/disco/pack/fd_pack_cost.h`, where `opt_loaded_accounts_data_cost` is added, and `src/app/fdctl/run/tiles/fd_bank.c`, where single consumed-CU accounting is replaced with separate execution and account-data CU accounting. `src/disco/pack/fd_pack.h` marks relevant cost constants as consensus critical. Unsupported claims removed: replay protection, signature validation vulnerability, invalid transaction execution, proven consensus failure, and quantified severity. Protocol security invariant: Transaction packing and bank-side accounting should use consistent cost components when applying block or vote cost limits. The provided evidence shows the patch tightening that accounting, but it does not establish that the prior mismatch created an exploitable security vulnerability or concrete consensus failure. Verification notes: No evidence that signature verification or replay protection logic was changed. No concrete exploit, adversarial transaction, or consensus-failure scenario is proven by the patch alone. The patch supports resource-accounting hardening, not authentication or authorization enforcement. The provided evidence does not prove that prior behavior allowed invalid transactions to execute. Economic impact, fee impact, and block overpacking severity are not quantified. No adversarial transaction or exploit scenario is provided. No evidence shows invalid transactions could execute. No evidence quantifies overpacking, fee, or consensus impact. Security relevance is plausible but not established by the supplied patch evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-accounting-mismatch`
Final impact type: `consensus-resource-accounting`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, resource-accounting, cost-model, validator, consensus`

The evidence supports retaining this as security-hardening, not as a concrete security-fix. The patch changes validator transaction packing and bank-side compute-unit accounting, explicitly separates loaded account data cost from execution cost, and touches code described as part of or adjacent to consensus-critical cost limits. That is enough to treat it as tightening security-sensitive resource accounting, but the original replay/signature framing is unsupported.

## Security Evidence

1. `fd_pack_compute_cost` gains an explicit `opt_loaded_accounts_data_cost` output.
2. Bank-side accounting changes from a single consumed CU value to separate execution and account-data CU values.
3. Actual consumed CUs are now computed as non-execution plus execution plus account-data cost.
4. Simple vote transactions receive explicit fixed-cost handling with zero account-data cost.
5. Nearby pack constants are described as consensus critical.

## Missing Evidence

1. No concrete exploit scenario is shown.
2. No evidence shows replay protection or signature validation was affected.
3. No proof that invalid transactions could execute before the patch.
4. No quantified impact for block overpacking, fee loss, or consensus divergence.
5. No commit body or advisory states this was a security vulnerability.

## Claim Boundaries

1. Validate only as resource-accounting hardening in a validator transaction packing path.
2. Do not claim a replay, request forgery, or signature-validation bug.
3. Do not claim a confirmed consensus split or exploitable vulnerability.
4. Do not claim economic impact beyond plausible cost-accounting risk.
