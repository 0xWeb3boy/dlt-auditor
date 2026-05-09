---
case_id: case_20200526_8c8e2c4b2b
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
confidence: high
source_quality: high
date: 2020-05-26
source_refs:
  - git:8c8e2c4b2b70669846150af5564135392b9eee51
  - "runtime/src/message_processor.rs:123"
  - "programs/bpf_loader/src/lib.rs:184"
  - "programs/bpf_loader/src/syscalls.rs:688"
  - "programs/bpf_loader/src/syscalls.rs:742"
bug_class: cross-program-invocation-privilege-escalation
impact_type:
  - privilege-escalation
  - authorization-bypass
  - state-integrity
tags:
  - blockchain-core
  - bpf-loader
  - cross-program-invocation
  - privilege-escalation
  - account-privilege-check
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch is a security fix for privilege escalation in Solana's BPF cross-program invocation path. The grounded evidence shows a new `verify_instruction` check in `programs/bpf_loader/src/syscalls.rs`, a call to that verification before callee message construction, and VM setup changed to pass caller parameter accounts so the syscall layer has the account privilege context needed for the check.

## Observed Patch Facts

1. In `runtime/src/message_processor.rs`, the patch replaces `pub fn verify_cross_program(` with `pub fn update(&mut self, account: &Account) {`.

2. In `programs/bpf_loader/src/lib.rs`, the patch replaces `let (mut vm, heap_region) = match create_vm(&program_account.data, invoke_context) {` with `let (mut vm, heap_region) =`.

3. In `programs/bpf_loader/src/syscalls.rs`, the patch replaces `/// Call process instruction, common to both Rust and C` with `fn verify_instruction<'a>(`.

4. In `programs/bpf_loader/src/syscalls.rs`, the patch replaces `let message = Message::new_with_payer(&[instruction], None);` with `let signers = syscall.translate_signers(`.

## Project Context

The changed code sits primarily in `runtime/src`, `programs/bpf_loader/src`, `programs/bpf_loader`, which anchors the finding in the `storage` area of the project. Historical context from `runtime/src/system_instruction_processor.rs`, `runtime/src/bank.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `runtime/src/system_instruction_processor.rs`. The strongest project-level identifiers around this patch are `instruction`, `syscall`, `Message::new_with_payer`, and `info`.

## Before/After Behavior

Before the patch, the provided evidence shows the BPF syscall `call` path translating an instruction and constructing a `Message::new_with_payer` without an evidenced pre-dispatch check that the invoked instruction's account metadata was bounded by the caller's keyed-account privileges. VM creation also did not receive `parameter_accounts` in the shown hunk. After the patch, VM creation receives `&parameter_accounts`, signer seeds are translated before dispatch, `verify_instruction(syscall, &instruction, &signers)?` is called, and only then is the callee message constructed.

# Root Cause

The BPF CPI syscall path lacked, or did not have sufficient context for, an early check that requested callee account privileges were limited to the caller's account privileges and valid signer derivations.

## Walkthrough

1. A BPF program enters the cross-program invocation syscall path.

2. The syscall translates the instruction supplied from VM memory.

3. The patched flow obtains the caller program id and translates signer seeds for that caller.

4. The new `verify_instruction` function reads caller keyed accounts from the syscall object.

5. The verification compares requested invoked-instruction account privileges against caller-side privileges and derived signers.

6. If the requested privileges are not allowed, the syscall returns an error before callee message construction and dispatch.

7. The loader now passes `parameter_accounts` into VM creation so the syscall layer can access caller account privilege context.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/syscalls.rs | 688 | Adds cross-program instruction privilege verification against caller keyed accounts and signer derivations. |
| programs/bpf_loader/src/syscalls.rs | 742 | Runs signer translation and instruction verification before building the callee message and invoking the target program. |
| programs/bpf_loader/src/lib.rs | 184 | Passes parameter accounts into BPF VM creation so syscall verification has caller account privilege context. |
| runtime/src/message_processor.rs | 123 | Previously hosted cross-program account privilege/post-state checks; now surrounding account snapshot update remains part of runtime account integrity handling. |

## Code Snippets

## Snippet 1

Context: `runtime/src/message_processor.rs:123` (changes signature or replay validation logic)

Before
```rust
}

    pub fn verify_cross_program(
        &self,
        is_writable: bool,
        is_signer: bool,
        signers: &[Pubkey],
        program_id: &Pubkey,
```
After
```rust
}

    pub fn update(&mut self, account: &Account) {
        self.lamports = account.lamports;
```

## Snippet 2

Context: `programs/bpf_loader/src/lib.rs:184` (changes a sensitive control or state-update path)

Before
```rust
{
            let program_account = program.try_account_ref_mut()?;
            let (mut vm, heap_region) = match create_vm(&program_account.data, invoke_context) {
                Ok(info) => info,
                Err(e) => {
                    warn!("Failed to create BPF VM: {}", e);
                    return Err(BPFLoaderError::VirtualMachineCreationFailed.into());
                }
```
After
```rust
{
            let program_account = program.try_account_ref_mut()?;
            let (mut vm, heap_region) =
                match create_vm(&program_account.data, &parameter_accounts, invoke_context) {
                    Ok(info) => info,
                    Err(e) => {
                        warn!("Failed to create BPF VM: {}", e);
                        return Err(BPFLoaderError::VirtualMachineCreationFailed.into());
```

## Snippet 3

Context: `programs/bpf_loader/src/syscalls.rs:688` (changes a sensitive control or state-update path)

Before
```rust
}

/// Call process instruction, common to both Rust and C
fn call<'a>(
```
After
```rust
}

fn verify_instruction<'a>(
    syscall: &dyn SyscallProcessInstruction<'a>,
    instruction: &Instruction,
    signers: &[Pubkey],
) -> Result<(), EbpfError<BPFError>> {
    let callers_keyed_accounts = syscall.get_callers_keyed_accounts();
```

## Snippet 4

Context: `programs/bpf_loader/src/syscalls.rs:742` (changes a sensitive control or state-update path)

Before
```rust
let instruction = syscall.translate_instruction(instruction_addr, ro_regions)?;
    let message = Message::new_with_payer(&[instruction], None);
    let callee_program_id_index = message.instructions[0].program_id_index as usize;
    let callee_program_id = message.account_keys[callee_program_id_index];
    let caller_program_id = invoke_context
        .get_caller()
        .map_err(SyscallError::InstructionError)?;
```
After
```rust
let instruction = syscall.translate_instruction(instruction_addr, ro_regions)?;
    let caller_program_id = invoke_context
        .get_caller()
        .map_err(SyscallError::InstructionError)?;
    let signers = syscall.translate_signers(
        caller_program_id,
        signers_seeds_addr,
```

# Fix Pattern

Add pre-dispatch privilege validation at the BPF CPI syscall boundary and thread caller account context into the VM/syscall layer.

## How It Was Fixed

`programs/bpf_loader/src/syscalls.rs` adds `verify_instruction`, calls it before constructing the callee `Message`, and uses translated signer seeds in that validation. `programs/bpf_loader/src/lib.rs` updates `create_vm` to receive `&parameter_accounts`, supporting access to caller privilege context.

# Why It Matters

1. CPI account metadata is a protocol security boundary.

2. A caller must not be able to upgrade readonly accounts to writable accounts for a callee.

3. A caller must not make nonsigner accounts appear signed except through valid signer derivation.

4. The evidence supports BPF CPI privilege escalation, not storage corruption, replay failure, or cryptographic failure.

# Evidence Notes

Strongest evidence is `programs/bpf_loader/src/syscalls.rs`, where `verify_instruction` is added with a privilege-escalation check and called before callee message construction, and `programs/bpf_loader/src/lib.rs`, where `parameter_accounts` are passed into VM creation. The `runtime/src/message_processor.rs` hunk is account-integrity-related context, but the provided evidence does not justify claiming the root cause was storage corruption or that the fix was a general runtime storage change. The evidence does not establish exploit mechanics, loss of funds, replay impact, or cryptographic impact. Protocol security invariant: During BPF cross-program invocation, the invoked instruction must not request account privileges beyond those available to the caller: readonly caller accounts must not be treated as writable, and nonsigner accounts must not become signers unless covered by accepted signer derivations for the caller program. Verification notes: Patch evidence does not prove a concrete exploit transaction or demonstrated loss of funds. Patch evidence does not show a cryptographic or replay-protection flaw despite heuristic labels. Patch evidence does not support classifying this as generic storage corruption. Patch evidence does not prove privilege escalation outside BPF cross-program invocation account metadata handling. Patch evidence does not establish whether all language bindings were exploitable, only that Rust/C BPF invocation paths and tests were updated. Commit subject explicitly says privilege escalation. Added code comments and function placement support a CPI privilege-boundary fix. Mapper's storage/state-corruption heuristic should be downgraded to BPF CPI privilege escalation. Keep in security corpus as a confirmed security fix based on the provided patch evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `cross-program-invocation-privilege-escalation`
Final impact type: `privilege-escalation, authorization-bypass, state-integrity`
Final tags: `blockchain-core, bpf-loader, cross-program-invocation, privilege-escalation, account-privilege-check`

The supplied evidence supports keeping this as a security fix, but not as a storage/state-corruption finding. The commit subject explicitly says privilege escalation, and the patch adds a pre-dispatch BPF cross-program invocation verification function that checks requested account privileges against caller account privileges and signer derivations before constructing and dispatching the callee message. The loader also threads parameter account context into VM creation so the syscall layer can perform that check.

## Security Evidence

1. Commit subject is "Prevent privilege escalation".
2. New `verify_instruction` function is added in `programs/bpf_loader/src/syscalls.rs`.
3. Added code comment states `Check for privilege escalation`.
4. The call path now translates signer seeds and invokes `verify_instruction(syscall, &instruction, &signers)?` before callee message construction.
5. VM creation now receives `&parameter_accounts`, giving syscall verification access to caller account privilege context.
6. Runtime evidence shows checks preventing readonly accounts from becoming writable.

## Missing Evidence

1. No concrete exploit transaction or proof-of-loss is provided.
2. No evidence supports the original storage, queue, snapshot, or generic state-corruption classification.
3. No evidence shows cryptographic or replay-protection impact.
4. No evidence establishes privilege escalation outside the BPF cross-program invocation account metadata path.

## Claim Boundaries

1. Validate as BPF cross-program invocation privilege-boundary enforcement.
2. Do not claim a storage subsystem vulnerability.
3. Do not claim demonstrated fund theft or chain compromise from the supplied patch alone.
4. Do not broaden beyond account writable/signer privilege escalation checks in CPI.
