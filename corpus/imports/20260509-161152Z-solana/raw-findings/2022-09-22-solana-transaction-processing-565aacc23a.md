---
case_id: case_20220922_565aacc23a
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
impact_type:
  - state-integrity
confidence: medium
source_quality: medium
date: 2022-09-22
source_refs:
  - git:565aacc23a4f9bfcc258e3ae5e75b911d2bbc9f8
  - "programs/bpf_loader/src/lib.rs:1070"
  - "transaction-status/src/parse_bpf_loader.rs:151"
  - "programs/bpf_loader/src/lib.rs:45"
  - "sdk/program/src/bpf_loader_upgradeable.rs:301"
bug_class: missing-account-mutability-check
tags:
  - blockchain-core
  - bpf-loader
  - account-mutability
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely hardens Solana's upgradeable BPF loader by changing the extension flow from a ProgramData-centered instruction to a Program-centered instruction and adding a runtime check that rejects the operation when the Program account is not writable. The evidence supports a missing writable-account enforcement issue, but does not establish a concrete exploit such as arbitrary ProgramData modification or privilege escalation.

## Observed Patch Facts

1. In `programs/bpf_loader/src/lib.rs`, the patch replaces `let old_len = programdata_account.get_data().len();` with `let program_account = instruction_context`.

2. In `transaction-status/src/parse_bpf_loader.rs`, the patch replaces `UpgradeableLoaderInstruction::ExtendProgramData { additional_bytes } => {` with `UpgradeableLoaderInstruction::ExtendProgram { additional_bytes } => {`.

3. In `programs/bpf_loader/src/lib.rs`, the patch replaces `enable_bpf_loader_extend_program_data_ix,` with `enable_bpf_loader_extend_program_ix, error_on_syscall_bpf_function_hash_collisions,`.

4. In `sdk/program/src/bpf_loader_upgradeable.rs`, the patch replaces `/// Returns the instruction required to extend the size of a program data account` with `/// Returns the instruction required to extend the size of a program's`.

## Project Context

The changed code sits primarily in `programs/bpf_loader/src`, `programs/bpf_loader`, `transaction-status/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `transaction-status/src/parse_accounts.rs`, `transaction-status/src/parse_instruction.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `transaction-status/src/parse_vote.rs`, `transaction-status/src/parse_token.rs`. The strongest project-level identifiers around this patch are `instruction`, `additional_bytes`, `accounts`, and `account`.

## Before/After Behavior

Before the patch, the provided loader hunk shows the extension flow validating ProgramData and proceeding toward resizing based on `programdata_account.get_data().len()` without shown enforcement that the associated Program account was writable. The SDK helper accepted a ProgramData address directly and the parser represented the instruction as `extendProgramData`. After the patch, the loader borrows `PROGRAM_ACCOUNT_INDEX`, rejects the instruction if `program_account.is_writable()` is false, and the API/parser semantics are aligned around `ExtendProgram` and an explicit Program account.

# Root Cause

The earlier instruction shape and validation path were centered on the ProgramData account. Based on the supplied evidence, the loader did not clearly require the associated Program account to be writable even though extending ProgramData changes executable state associated with that Program account.

## Walkthrough

1. A caller used the earlier ProgramData-oriented extension instruction shape.

2. The loader validated the ProgramData account and proceeded toward calculating the new data length.

3. The supplied pre-patch evidence does not show a Program account borrow or writable check before that downstream extension work.

4. The patch changes the operation to `ExtendProgram`, making the Program account explicit.

5. The runtime now borrows the Program account and returns `InstructionError::InvalidArgument` if it is not writable.

6. SDK and transaction-status parsing were updated to match the new Program-centered instruction semantics.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/lib.rs | 1070 | runtime loader enforcement for ExtendProgram account mutability, ownership, and Program state validation |
| sdk/program/src/bpf_loader_upgradeable.rs | 301 | client instruction constructor now takes a Program address and derives the ProgramData address, adding the Program account to metas |
| sdk/program/src/loader_upgradeable_instruction.rs | 1 | upgradeable loader instruction definition updated from ExtendProgramData toward ExtendProgram semantics |
| transaction-status/src/parse_bpf_loader.rs | 151 | transaction status parser updated to parse ExtendProgram accounts and labels consistently |
| sdk/src/feature_set.rs | 1 | feature gate renamed/enabled for the ExtendProgram instruction path |

## Code Snippets

## Snippet 1

Context: `programs/bpf_loader/src/lib.rs:1070` (changes a sensitive control or state-update path)

Before
```rust
}

            let old_len = programdata_account.get_data().len();
            let new_len = old_len.saturating_add(additional_bytes as usize);
```
After
```rust
}

            let program_account = instruction_context
                .try_borrow_instruction_account(transaction_context, PROGRAM_ACCOUNT_INDEX)?;
            if !program_account.is_writable() {
                ic_logger_msg!(log_collector, "Program account is not writable");
                return Err(InstructionError::InvalidArgument);
            }
```

## Snippet 2

Context: `transaction-status/src/parse_bpf_loader.rs:151` (changes a sensitive control or state-update path)

Before
```rust
})
        }
        UpgradeableLoaderInstruction::ExtendProgramData { additional_bytes } => {
            check_num_bpf_upgradeable_loader_accounts(&instruction.accounts, 2)?;
            Ok(ParsedInstructionEnum {
                instruction_type: "extendProgramData".to_string(),
                info: json!({
                    "additionalBytes": additional_bytes,
```
After
```rust
})
        }
        UpgradeableLoaderInstruction::ExtendProgram { additional_bytes } => {
            check_num_bpf_upgradeable_loader_accounts(&instruction.accounts, 2)?;
            Ok(ParsedInstructionEnum {
                instruction_type: "extendProgram".to_string(),
                info: json!({
                    "additionalBytes": additional_bytes,
```

## Snippet 3

Context: `programs/bpf_loader/src/lib.rs:45` (changes a sensitive control or state-update path)

Before
```rust
disable_bpf_deprecated_load_instructions, disable_bpf_unresolved_symbols_at_runtime,
            disable_deploy_of_alloc_free_syscall, disable_deprecated_loader,
            enable_bpf_loader_extend_program_data_ix,
            error_on_syscall_bpf_function_hash_collisions, reject_callx_r10,
        },
        instruction::{AccountMeta, InstructionError},
```
After
```rust
disable_bpf_deprecated_load_instructions, disable_bpf_unresolved_symbols_at_runtime,
            disable_deploy_of_alloc_free_syscall, disable_deprecated_loader,
            enable_bpf_loader_extend_program_ix, error_on_syscall_bpf_function_hash_collisions,
            reject_callx_r10,
        },
        instruction::{AccountMeta, InstructionError},
```

## Snippet 4

Context: `sdk/program/src/bpf_loader_upgradeable.rs:301` (changes a sensitive control or state-update path)

Before
```rust
}

/// Returns the instruction required to extend the size of a program data account
pub fn extend_program_data(
    program_data_address: &Pubkey,
    payer_address: Option<&Pubkey>,
    additional_bytes: u32,
) -> Instruction {
```
After
```rust
}

/// Returns the instruction required to extend the size of a program's
/// executable data account
pub fn extend_program(
    program_address: &Pubkey,
    payer_address: Option<&Pubkey>,
    additional_bytes: u32,
```

# Fix Pattern

Add explicit account metadata validation in the runtime loader before continuing with executable data extension, and align client/parser instruction semantics with the stricter account model.

## How It Was Fixed

The loader now borrows the Program account at `PROGRAM_ACCOUNT_INDEX`, checks `program_account.is_writable()`, logs `Program account is not writable`, and rejects the instruction with `InstructionError::InvalidArgument` when the account is not writable. Supporting SDK and parser changes rename and relabel the operation from `ExtendProgramData` to `ExtendProgram` and include the Program account in the expected account model.

# Why It Matters

1. Enforces writable metadata for the Program account affected by executable data extension.

2. Keeps account mutability and runtime locking expectations aligned with loader behavior.

3. Reduces ambiguity between resizing a raw ProgramData account and extending a Program's executable data.

4. Evidence supports hardening, not a proven direct exploit.

# Evidence Notes

The strongest evidence is the runtime change in `programs/bpf_loader/src/lib.rs` adding a borrow of `PROGRAM_ACCOUNT_INDEX` and an `is_writable()` check. The SDK constructor and transaction-status parser changes support the shift from ProgramData-oriented to Program-oriented semantics. The supplied evidence does not prove arbitrary writes, authority bypass, privilege escalation, or the exact consequence of omitting the Program writable flag. Protocol security invariant: Upgradeable BPF loader instructions that extend a program's executable data should require the associated Program account to be present and declared writable, so runtime account metadata and locking reflect the executable program state being changed. Verification notes: The patch does not prove arbitrary ProgramData modification without normal authority checks. The patch does not show a direct privilege-escalation exploit. The transaction-status parser changes are representational and not independently security-relevant. The SDK/API rename alone would be non-security without the loader writable-account enforcement. The exact runtime consequence of omitting the writable Program account is not fully demonstrated by the provided evidence. No independent file inspection or command execution was used. Classification is limited to the provided commit metadata, hunks, mapper output, and draft. Parser and SDK changes are treated as supporting alignment, not as independent vulnerability fixes. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-account-mutability-check`
Final tags: `blockchain-core, bpf-loader, account-mutability, state-integrity`

The supplied patch evidence supports retaining this as security hardening, not a proven exploit fix. The runtime loader now explicitly requires the Program account to be writable before extending executable program data, and the SDK/parser changes align the instruction model around the Program account rather than only ProgramData. In a blockchain loader path, account mutability and locking are security-sensitive state integrity controls, but the evidence does not prove arbitrary modification, privilege escalation, or concrete state corruption.

## Security Evidence

1. Runtime code adds a borrow of PROGRAM_ACCOUNT_INDEX before continuing the extend operation.
2. Runtime code rejects the instruction when program_account.is_writable() is false.
3. The check is in the upgradeable BPF loader path for extending executable program data.
4. SDK changes move the API from a ProgramData address to a Program address and derive ProgramData from it.
5. Parser and feature-gate changes consistently rename the operation from ExtendProgramData to ExtendProgram.

## Missing Evidence

1. No exploit scenario is shown.
2. No evidence proves unauthorized ProgramData modification without existing authority checks.
3. No evidence shows a direct privilege escalation or arbitrary write primitive.
4. The exact consequence of omitting the Program account writable flag is not demonstrated.

## Claim Boundaries

1. Validate only as security hardening, not as a confirmed vulnerability fix.
2. Do not claim proven state corruption from the supplied hunks.
3. Do not treat parser or SDK renaming as independently security-relevant.
4. The supported claim is limited to stricter account mutability enforcement in a sensitive loader path.
