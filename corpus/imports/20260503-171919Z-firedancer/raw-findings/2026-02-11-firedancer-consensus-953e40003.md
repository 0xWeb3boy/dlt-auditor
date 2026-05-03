---
case_id: case_20260211_953e40003
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2026-02-11
source_refs:
  - git:953e40003afa9a6dd648fcbc08f19be405f77987
  - "src/flamenco/vm/syscall/Local.mk:14"
  - "src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c:633"
  - "src/flamenco/vm/syscall/test_cpi_shared_data_addr.c:1"
bug_class: missing-bounds-check-buffer-overflow
impact_type:
  - memory-safety
  - memory-corruption
confidence: high
tags:
  - blockchain-core
  - vm-syscall
  - cpi
  - missing-bounds-check
  - buffer-overflow
  - memory-safety
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

Commit 953e40003 adds a missing destination-length check in Flamenco's CPI UPDATE_CALLER_ACCOUNT path. Before copying `post_len` bytes from callee account data back into `caller_account->serialized_data`, the code now verifies that `caller_account->serialized_data_len == post_len` and returns `FD_EXECUTOR_INSTR_ERR_ACC_DATA_TOO_SMALL` on mismatch. The added regression test documents a shared `data_box_addr` scenario that can leave `serialized_data_len` stale and otherwise lead to a buffer overflow on the final memcpy.

## Observed Patch Facts

1. In `src/flamenco/vm/syscall/Local.mk`, the patch adds `$(call make-unit-test,test_cpi_shared_data_addr,test_cpi_shared_data_addr,fd_flamenco...`.

2. In `src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c`, the patch replaces `fd_memcpy( caller_account->serialized_data, fd_account_data( callee_meta ), post_len );` with `/* https://github.com/anza-xyz/agave/blob/v3.0.4/syscalls/src/cpi.rs#L1261-L1263 */`.

3. In `src/flamenco/vm/syscall/test_cpi_shared_data_addr.c`, the commit introduces a new helper or container type around `/* Unit test for a CPI bug which was reported and fixed` to support the wider fix.

## Project Context

The changed code sits primarily in `src/flamenco/vm/syscall`, `src/flamenco/vm`, which anchors the finding in the `consensus` area of the project. Historical context from `src/flamenco/vm/syscall/test_vm_syscalls.c`, `src/flamenco/vm/syscall/test_vm_syscall_curve.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/flamenco/vm/syscall/test_vm_syscalls.c`, `src/flamenco/vm/syscall/test_vm_syscall_curve.c`. The strongest project-level identifiers around this patch are `test`, `call`, `unit`, and `test_vm_increase_cpi_account_info_limit`. Nearby tests or test-like files include `src/flamenco/vm/instr_test/v2/jump.instr`, `src/flamenco/vm/instr_test/v0/jump.instr`.

## Before/After Behavior

Before the patch, the non-direct-mapping CPI copy-back branch copied `post_len` bytes into `caller_account->serialized_data` without the shown final check that the destination serialized length still matched `post_len`. The added test describes a case where shared account length metadata can cause a later account update to skip resizing, leaving stale destination length metadata. After the patch, the branch checks `caller_account->serialized_data_len != post_len` and returns `FD_EXECUTOR_INSTR_ERR_ACC_DATA_TOO_SMALL` instead of continuing to the copy in that mismatched state. The new unit test is registered in `Local.mk`.

# Root Cause

`UPDATE_CALLER_ACCOUNT` relied on earlier resize and length-tracking logic before performing the copy-back, but a shared `data_box_addr` case could make that metadata stale. Without revalidating the serialized destination length at the point of copy, the code could attempt to write `post_len` bytes into a buffer whose recorded serialized length did not match.

## Walkthrough

1. The non-direct-mapping CPI update path needs to copy callee account data back into the caller's serialized account buffer.

2. The pre-patch snippet shows this branch directly calling `fd_memcpy( caller_account->serialized_data, fd_account_data( callee_meta ), post_len );`.

3. The added test describes two accounts sharing the same `data_box_addr`.

4. The callee grows both accounts.

5. Updating the first account mutates the shared `ref_to_len_in_vm`.

6. The second account update then sees `prev_len == post_len`, skips the resize branch, and leaves `serialized_data_len` stale.

7. Without the new check, the final copy can proceed with `post_len` despite stale destination length metadata.

8. The fix rejects the mismatch with `FD_EXECUTOR_INSTR_ERR_ACC_DATA_TOO_SMALL` before the copy-back can proceed.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c | 633 | Adds the missing serialized_data_len versus post_len check before copying callee account data back to the caller buffer in non-direct-mapping CPI update. |
| src/flamenco/vm/syscall/test_cpi_shared_data_addr.c | 1 | Regression test documents and exercises the shared data_box_addr stale-length scenario that could lead to overflow on final memcpy. |
| src/flamenco/vm/syscall/Local.mk | 14 | Registers the new CPI shared-data-address unit test in the VM syscall test suite. |

## Code Snippets

## Snippet 1

Context: `src/flamenco/vm/syscall/Local.mk:14` (updates aggregate accounting or lifecycle state)

Before
```text
$(call make-unit-test,test_vm_increase_cpi_account_info_limit,test_vm_increase_cpi_account_info_limit,fd_flamenco fd_funk fd_util fd_ballet)
$(call run-unit-test,test_vm_increase_cpi_account_info_limit)
endif
endif
```
After
```text
$(call make-unit-test,test_vm_increase_cpi_account_info_limit,test_vm_increase_cpi_account_info_limit,fd_flamenco fd_funk fd_util fd_ballet)
$(call run-unit-test,test_vm_increase_cpi_account_info_limit)
$(call make-unit-test,test_cpi_shared_data_addr,test_cpi_shared_data_addr,fd_flamenco fd_funk fd_util fd_ballet)
$(call run-unit-test,test_cpi_shared_data_addr)
endif
endif
```

## Snippet 2

Context: `src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c:633` (updates aggregate accounting or lifecycle state)

Before
```c
https://github.com/anza-xyz/agave/blob/v3.0.4/syscalls/src/cpi.rs#L1254-L1265 */
  if( !(vm->stricter_abi_and_runtime_constraints && vm->direct_mapping) ) {
    fd_memcpy( caller_account->serialized_data, fd_account_data( callee_meta ), post_len );
  }
```
After
```c
https://github.com/anza-xyz/agave/blob/v3.0.4/syscalls/src/cpi.rs#L1254-L1265 */
  if( !(vm->stricter_abi_and_runtime_constraints && vm->direct_mapping) ) {

    /* https://github.com/anza-xyz/agave/blob/v3.0.4/syscalls/src/cpi.rs#L1261-L1263 */
    if( FD_UNLIKELY( caller_account->serialized_data_len!=post_len ) ) {
      FD_VM_ERR_FOR_LOG_INSTR( vm, FD_EXECUTOR_INSTR_ERR_ACC_DATA_TOO_SMALL );
      return FD_EXECUTOR_INSTR_ERR_ACC_DATA_TOO_SMALL;
    }
```

## Snippet 3

Context: `src/flamenco/vm/syscall/test_cpi_shared_data_addr.c:1` (updates aggregate accounting or lifecycle state)

Before
```c
(no before snippet captured)
```
After
```c
/* Unit test for a CPI bug which was reported and fixed

   Scenario:
   - Two accounts share the same data_box_addr
   - The callee grows both accounts
   - The first account's update modifies the shared ref_to_len_in_vm,
     causing the second account's update to skip the resize branch
     (since prev_len == post_len).
```

# Fix Pattern

Validate the destination buffer length immediately before the memory copy in the CPI copy-back path, rather than relying solely on earlier resize decisions or shared length metadata.

## How It Was Fixed

The patch adds a check inside `src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c` in the non-direct-mapping branch: if `caller_account->serialized_data_len != post_len`, it logs and returns `FD_EXECUTOR_INSTR_ERR_ACC_DATA_TOO_SMALL`. It also adds and registers `test_cpi_shared_data_addr` to cover the shared-data-address stale-length scenario.

# Why It Matters

1. Prevents a documented stale-length CPI state from reaching the final copy-back memcpy.

2. Converts a mismatched destination length into an explicit VM instruction error.

3. Protects a VM syscall path that handles account data during CPI.

4. Keeps Firedancer behavior aligned with the cited Agave check.

# Evidence Notes

Supported by the implementation change in `src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c`, which adds the `serialized_data_len != post_len` check and error return; by the added test comment in `src/flamenco/vm/syscall/test_cpi_shared_data_addr.c`, which states the shared `data_box_addr` stale-length scenario can result in a buffer overflow on final memcpy; and by `Local.mk`, which registers the new regression test. The evidence does not establish remote exploitability, code execution, privilege bypass, direct-mapping impact, consensus divergence, or network-wide impact. Protocol security invariant: During non-direct-mapping CPI caller-account update, the VM must not copy post-call account data into the caller serialized-data buffer unless the destination serialized_data_len matches the post-call data length. A stale or mismatched destination length must abort with an account-data-too-small error before memcpy. Verification notes: The patch does not prove remote exploitability or attacker-controlled code execution. The patch does not show an access-control or privilege-bypass fix. The affected failing path is the non-direct-mapping copy-back branch; direct-mapping behavior is not shown as vulnerable here. The evidence supports possible buffer overflow during memcpy, but does not prove a consensus divergence outcome. The patch aligns with Agave behavior, but the provided evidence does not independently prove network-wide impact. No external exploitability claim is supported by the provided evidence. Direct-mapping behavior is outside the shown vulnerable path. The helper test file is supporting regression coverage, not the root cause. The security classification rests on the documented buffer-overflow risk and the added pre-memcpy bounds check. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `missing-bounds-check-buffer-overflow`
Final impact type: `memory-safety, memory-corruption`
Final confidence: `high`
Final tags: `blockchain-core, vm-syscall, cpi, missing-bounds-check, buffer-overflow, memory-safety`

The supplied patch evidence supports a security-fix classification, but the original consensus/accounting/economic framing is too strong. The implementation adds a missing length check immediately before copying `post_len` bytes into `caller_account->serialized_data`, and the new regression test explicitly documents that the stale-length shared-data-address scenario can result in a buffer overflow on the final memcpy. The evidence supports a memory-safety fix in a VM CPI syscall path, not a proven consensus, economic, privilege, or remote-code-execution impact.

## Security Evidence

1. Patch adds `caller_account->serialized_data_len != post_len` guard before the CPI copy-back memcpy.
2. Mismatch now returns `FD_EXECUTOR_INSTR_ERR_ACC_DATA_TOO_SMALL` instead of proceeding to copy.
3. Added test comment describes stale `serialized_data_len` caused by shared `data_box_addr`.
4. Test comment states the stale-length condition can result in a buffer overflow on the final memcpy.
5. New unit test is registered alongside the implementation change.

## Missing Evidence

1. No proof of remote exploitability or attacker-controlled code execution.
2. No evidence of privilege bypass or access-control failure.
3. No evidence that the issue causes consensus divergence or economic distortion.
4. No complete before/after test body proving exact allocation sizes or overwrite extent.
5. Direct-mapping behavior is not shown to be vulnerable.

## Claim Boundaries

1. Classify as a CPI VM memory-safety bounds-check fix.
2. Do not claim confirmed consensus or economic impact from the supplied evidence.
3. Do not claim remote exploitability, RCE, or privilege escalation.
4. Affected path is the non-direct-mapping CPI caller-account update copy-back branch.
5. The regression test is supporting evidence; the core fix is the pre-memcpy destination-length check.
