---
case_id: case_20250321_f35407b68
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2025-03-21
source_refs:
  - git:f35407b68d2db3f892707dbc02025e60b2a1242c
  - "src/flamenco/runtime/context/fd_exec_txn_ctx.h:145"
  - "src/flamenco/features/feature_map.json:147"
  - "src/flamenco/runtime/context/fd_exec_txn_ctx.c:235"
  - "src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c:862"
bug_class: memory-lifetime
impact_type:
  - memory-safety
tags:
  - blockchain-core
  - vm
  - cpi
  - memory-lifetime
  - memory-safety
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant memory lifetime bug in Flamenco's CPI syscall path. The core change replaces a stack-local `fd_instr_info_t instruction_to_execute[1]` with transaction-owned `txn_ctx->cpi_instr_infos[txn_ctx->cpi_instr_info_cnt++]`, adds that storage to the transaction context, and initializes the counter during transaction setup. The evidence supports a use-after-scope style memory corruption fix, but does not establish exploitability, consensus impact, arbitrary code execution, or attacker control beyond the CPI execution path.

## Observed Patch Facts

1. In `src/flamenco/runtime/context/fd_exec_txn_ctx.h`, the patch replaces `fd_exec_instr_trace_entry_t instr_trace[FD_MAX_INSTRUCTION_TRACE_LENGTH]; /* Instruct...` with `/* These instr infos are statically allocated at the beginning of a transaction`.

2. In `src/flamenco/features/feature_map.json`, the patch replaces `{"name":"deplete_cu_meter_on_vm_failure","pubkey": "B7H2caeia4ZFcpE3QcgMqbiWiBtWrdBRB...` with `{"name":"deplete_cu_meter_on_vm_failure","pubkey": "B7H2caeia4ZFcpE3QcgMqbiWiBtWrdBRB...`.

3. In `src/flamenco/runtime/context/fd_exec_txn_ctx.c`, the patch replaces `txn_ctx->instr_info_cnt = 0;` with `txn_ctx->instr_info_cnt = 0UL;`.

4. In `src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c`, the patch replaces `fd_instr_info_t instruction_to_execute[ 1 ];` with `fd_instr_info_t * instruction_to_execute = &vm->instr_ctx->txn_ctx->cpi_instr_infos[...`.

## Project Context

The changed code sits primarily in `src/flamenco/runtime/context`, `src/flamenco/runtime`, `src/flamenco/features`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/flamenco/vm/syscall/fd_vm_syscall_cpi.c`, `src/flamenco/vm/syscall/fd_vm_syscall.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/flamenco/runtime/fd_executor.c`, `src/flamenco/runtime/info/fd_instr_info.h`. The strongest project-level identifiers around this patch are `txn_ctx`, `name`, `pubkey`, and `instr_info_cnt`. Nearby tests or test-like files include `src/flamenco/runtime/tests/fd_exec_instr_test.c`, `src/flamenco/runtime/tests/fd_dump_pb.h`.

## Before/After Behavior

Before the patch, CPI instruction metadata was created in a stack-local `fd_instr_info_t instruction_to_execute[1]` inside the CPI syscall entrypoint and then passed into instruction translation/execution logic. After the patch, CPI instruction metadata is allocated from transaction-owned `cpi_instr_infos`, with a transaction-scoped counter reset at transaction setup. A new comment explains that these instruction infos are kept at transaction level because VM syscalls such as `GetProcessedSiblingInstruction()` may refer to earlier processed instructions.

# Root Cause

CPI instruction metadata was allocated with syscall stack-frame lifetime even though later VM behavior may refer back to processed instruction metadata during the same transaction.

## Walkthrough

1. The CPI syscall translates CPI ABI inputs into the runtime instruction format.

2. Before the patch, the translated CPI instruction info lived in a stack-local `fd_instr_info_t instruction_to_execute[1]`.

3. The transaction context comment added by the patch says VM syscalls may refer to instructions processed earlier in the transaction.

4. A stack-local instruction info can become invalid once the CPI syscall frame returns if later transaction-level references still point to it.

5. The fix adds transaction-owned `cpi_instr_infos[FD_MAX_INSTRUCTION_TRACE_LENGTH]` and `cpi_instr_info_cnt`.

6. The CPI syscall now obtains instruction metadata from transaction-owned storage and increments the counter.

7. Transaction setup resets `cpi_instr_info_cnt` for each transaction.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c | 862 | CPI syscall creates the instruction info used to execute translated CPI inputs; allocation moved from stack-local storage to transaction-owned CPI instruction storage. |
| src/flamenco/runtime/context/fd_exec_txn_ctx.h | 145 | Transaction context gains `cpi_instr_infos` and `cpi_instr_info_cnt` storage so CPI instruction metadata can outlive the syscall stack frame. |
| src/flamenco/runtime/context/fd_exec_txn_ctx.c | 235 | Transaction setup initializes the CPI instruction info counter for each transaction. |
| src/flamenco/features/feature_map.json | 147 | Ancillary feature-map comment affecting fuzzing behavior for VM failure metering; not the core vulnerability path. |

## Code Snippets

## Snippet 1

Context: `src/flamenco/runtime/context/fd_exec_txn_ctx.h:145` (changes a sensitive control or state-update path)

Before
```c
ulong                       instr_info_cnt;

  fd_exec_instr_trace_entry_t instr_trace[FD_MAX_INSTRUCTION_TRACE_LENGTH]; /* Instruction trace */
  ulong                       instr_trace_length;                           /* Number of instructions in the trace */
```
After
```c
ulong                       instr_info_cnt;

  /* These instr infos are statically allocated at the beginning of a transaction
     and are only written to / referred to within the VM. It's kept
     at the transaction level because syscalls like `GetProcessedSiblingInstruction()`
     may refer to instructions processed earlier in the transaction. */
  fd_instr_info_t             cpi_instr_infos[FD_MAX_INSTRUCTION_TRACE_LENGTH];
  ulong                       cpi_instr_info_cnt;
```

## Snippet 2

Context: `src/flamenco/features/feature_map.json:147` (changes a sensitive control or state-update path)

Before
```text
{"name":"delay_visibility_of_program_deployment","pubkey": "GmuBvtFb2aHfSfMXpuFeWZGHyDeCLPS79s48fmCWCfM5","cleaned_up":[1,18,0],"activated_on_all_clusters":1},
  {"name":"apply_cost_tracker_during_replay","pubkey": "2ry7ygxiYURULZCrypHhveanvP5tzZ4toRwVp89oCNSj"},
  {"name":"deplete_cu_meter_on_vm_failure","pubkey": "B7H2caeia4ZFcpE3QcgMqbiWiBtWrdBRBSJ1DY6Ktxbq"},
  {"name":"bpf_account_data_direct_mapping","pubkey": "AjX3A4Nv2rzUuATEUWLP4rrBaBropyUnHxEvFDj1dKbx","old": "GJVDwRkUPNdk9QaK4VsU4g1N41QNxhy1hevjf8kz45Mq"},
  {"name":"add_set_tx_loaded_accounts_data_size_instruction","pubkey": "G6vbf1UBok8MWb8m25ex86aoQHeKTzDKzuZADHkShqm6","cleaned_up":[1,18,0],"activated_on_all_clusters":1},
```
After
```text
{"name":"delay_visibility_of_program_deployment","pubkey": "GmuBvtFb2aHfSfMXpuFeWZGHyDeCLPS79s48fmCWCfM5","cleaned_up":[1,18,0],"activated_on_all_clusters":1},
  {"name":"apply_cost_tracker_during_replay","pubkey": "2ry7ygxiYURULZCrypHhveanvP5tzZ4toRwVp89oCNSj"},
  {"name":"deplete_cu_meter_on_vm_failure","pubkey": "B7H2caeia4ZFcpE3QcgMqbiWiBtWrdBRBSJ1DY6Ktxbq","comment":"do not set activated_on_all_clusters for this - it significantly degrades vm fuzzing discovery"},
  {"name":"bpf_account_data_direct_mapping","pubkey": "AjX3A4Nv2rzUuATEUWLP4rrBaBropyUnHxEvFDj1dKbx","old": "GJVDwRkUPNdk9QaK4VsU4g1N41QNxhy1hevjf8kz45Mq"},
  {"name":"add_set_tx_loaded_accounts_data_size_instruction","pubkey": "G6vbf1UBok8MWb8m25ex86aoQHeKTzDKzuZADHkShqm6","cleaned_up":[1,18,0],"activated_on_all_clusters":1},
```

## Snippet 3

Context: `src/flamenco/runtime/context/fd_exec_txn_ctx.c:235` (changes a sensitive control or state-update path)

Before
```c
txn_ctx->capture_ctx     = NULL;

  txn_ctx->instr_info_cnt     = 0;
  txn_ctx->instr_trace_length = 0;

  txn_ctx->exec_err      = 0;
```
After
```c
txn_ctx->capture_ctx     = NULL;

  txn_ctx->instr_info_cnt     = 0UL;
  txn_ctx->cpi_instr_info_cnt = 0UL;
  txn_ctx->instr_trace_length = 0UL;

  txn_ctx->exec_err      = 0;
```

## Snippet 4

Context: `src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c:862` (changes a sensitive control or state-update path)

Before
```c
/* Create the instruction to execute (in the input format the FD runtime expects) from
     the translated CPI ABI inputs. */
  fd_instr_info_t instruction_to_execute[ 1 ];

  err = VM_SYSCALL_CPI_INSTRUCTION_TO_INSTR_FUNC( vm, cpi_instruction, cpi_account_metas, program_id, data, instruction_to_execute );
```
After
```c
/* Create the instruction to execute (in the input format the FD runtime expects) from
     the translated CPI ABI inputs. */
  fd_instr_info_t * instruction_to_execute = &vm->instr_ctx->txn_ctx->cpi_instr_infos[ vm->instr_ctx->txn_ctx->cpi_instr_info_cnt++ ];

  err = VM_SYSCALL_CPI_INSTRUCTION_TO_INSTR_FUNC( vm, cpi_instruction, cpi_account_metas, program_id, data, instruction_to_execute );
```

# Fix Pattern

Move metadata with post-call references from stack-local storage into an owner whose lifetime covers all later references, and initialize the owner-scoped allocation counter during setup.

## How It Was Fixed

The patch adds `cpi_instr_infos` and `cpi_instr_info_cnt` to `fd_exec_txn_ctx_t`, initializes `cpi_instr_info_cnt` in `fd_exec_txn_ctx_setup_basic`, and changes the CPI syscall entrypoint to allocate `instruction_to_execute` from `vm->instr_ctx->txn_ctx->cpi_instr_infos` instead of the stack.

# Why It Matters

1. Fixes a concrete memory-lifetime mismatch in CPI instruction handling.

2. Keeps CPI instruction metadata valid for later transaction-level VM references.

3. Affects a critical VM transaction execution path.

4. Exploitability and consensus impact are not proven by the supplied evidence.

# Evidence Notes

Strongest evidence is in `src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c:862`, where stack-local CPI instruction info is replaced with transaction-owned storage; `src/flamenco/runtime/context/fd_exec_txn_ctx.h:145`, where `cpi_instr_infos` and `cpi_instr_info_cnt` are added with a lifetime comment; and `src/flamenco/runtime/context/fd_exec_txn_ctx.c:235`, where the counter is initialized. The `feature_map.json` change only adds a fuzzing-related comment and is not evidence of the memory corruption root cause. Protocol security invariant: CPI instruction metadata that may be referenced after a CPI syscall returns must have transaction-level lifetime, not stack-frame lifetime. Verification notes: The patch does not prove arbitrary code execution. The patch does not show a concrete attacker-controlled exploit path. The patch does not prove consensus divergence or ledger corruption. The provided hunks do not show bounds enforcement for `cpi_instr_info_cnt`. The feature-map comment appears fuzzing-related and is not evidence of the memory corruption root cause. The supplied evidence supports a memory lifetime bug, not arbitrary code execution. No concrete attacker-controlled exploit path is shown. No consensus divergence or ledger corruption is proven. Bounds enforcement for `cpi_instr_info_cnt` is not shown in the supplied hunks. The feature-map comment should be treated as ancillary, not part of the vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `memory-lifetime`
Final impact type: `memory-safety`
Final tags: `blockchain-core, vm, cpi, memory-lifetime, memory-safety`

The supplied evidence supports a real memory-lifetime fix in a security-sensitive VM/CPI execution path: CPI instruction metadata moved from stack-local storage to transaction-owned storage because later VM syscalls may refer to earlier processed instructions. That is enough to retain as security hardening, but the patch alone does not prove a concrete exploitable vulnerability, consensus failure, or ledger/state-integrity impact, so the original security-fix and state-integrity framing is too strong.

## Security Evidence

1. Commit subject explicitly says it fixes a memory corruption bug in CPI instruction info allocation.
2. CPI syscall changed from stack-local fd_instr_info_t storage to transaction-scoped cpi_instr_infos storage.
3. Transaction context comment states processed instruction infos may be referenced later by VM syscalls such as GetProcessedSiblingInstruction().
4. Transaction setup now initializes cpi_instr_info_cnt, supporting the new transaction-lifetime allocation model.

## Missing Evidence

1. No concrete exploit path or attacker-controlled trigger is shown.
2. No proof of consensus divergence, ledger corruption, or state-integrity violation is provided.
3. No bounds enforcement for cpi_instr_info_cnt is shown in the supplied evidence.
4. Test changes are listed but not shown with assertions proving the security impact.

## Claim Boundaries

1. Validate as memory-safety hardening in the VM/CPI path, not as confirmed exploitable vulnerability.
2. Do not claim arbitrary code execution or consensus impact from this evidence.
3. Do not treat the feature_map.json fuzzing comment as part of the core security fix.
4. State-integrity and replay tags are not supported by the shown patch alone.
