---
case_id: case_20200526_03abd3ddd7
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
  - git:03abd3ddd70b1e362098be5bbf253e4169891d4c
  - "runtime/src/message_processor.rs:123"
  - "programs/bpf_loader/src/lib.rs:184"
  - "programs/bpf_loader/src/syscalls.rs:688"
  - "programs/bpf_loader/src/syscalls.rs:742"
bug_class: missing-privilege-check
impact_type:
  - privilege-escalation
  - state-integrity
tags:
  - blockchain-core
  - bpf-loader
  - cross-program-invocation
  - privilege-escalation
  - access-control
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

Commit 03abd3ddd7 is supported as a security fix for Solana's BPF cross-program invocation path. The strongest evidence is the new verify_instruction helper in programs/bpf_loader/src/syscalls.rs, explicitly introduced with a privilege-escalation check and invoked before Message construction and dispatch.

## Observed Patch Facts

1. In `runtime/src/message_processor.rs`, the patch replaces `pub fn verify_cross_program(` with `pub fn update(&mut self, account: &Account) {`.

2. In `programs/bpf_loader/src/lib.rs`, the patch replaces `let (mut vm, heap_region) = match create_vm(&program_account.data, invoke_context) {` with `let (mut vm, heap_region) =`.

3. In `programs/bpf_loader/src/syscalls.rs`, the patch replaces `/// Call process instruction, common to both Rust and C` with `fn verify_instruction<'a>(`.

4. In `programs/bpf_loader/src/syscalls.rs`, the patch replaces `let message = Message::new_with_payer(&[instruction], None);` with `let signers = syscall.translate_signers(`.

## Project Context

The changed code sits primarily in `runtime/src`, `programs/bpf_loader/src`, `programs/bpf_loader`, which anchors the finding in the `storage` area of the project. Historical context from `runtime/src/system_instruction_processor.rs`, `runtime/src/bank.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `runtime/src/system_instruction_processor.rs`. The strongest project-level identifiers around this patch are `instruction`, `syscall`, `Message::new_with_payer`, and `info`.

## Before/After Behavior

Before the patch, the shown syscall path translated the invoked instruction and built a Message for dispatch without the added verify_instruction step. After the patch, it obtains the caller program id, translates signer seeds into a signer list, calls verify_instruction(syscall, &instruction, &signers), and only then constructs the Message. The create_vm signature also gains parameter_accounts, but the provided evidence does not establish that as the root cause.

# Root Cause

The supported root cause is missing or insufficient instruction-level privilege validation in the BPF CPI syscall path before dispatch. The evidence does not support the earlier storage/state-corruption framing.

## Walkthrough

1. A BPF program enters the syscall path for cross-program invocation.

2. The syscall translates the instruction supplied from VM memory.

3. The patched path obtains the caller program id and translates signer seeds into a signer list.

4. The new verify_instruction helper reads the caller's keyed accounts and iterates over the invoked instruction accounts.

5. The helper is explicitly introduced with a comment indicating it checks for privilege escalation.

6. The call path invokes verify_instruction before constructing the Message used for dispatch.

7. If verification fails, dispatch is blocked before the callee instruction is built and invoked.

8. Other touched files appear to support or align the CPI/account verification path, but the core security evidence is in programs/bpf_loader/src/syscalls.rs.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/syscalls.rs | 688 | adds cross-program invocation privilege verification against caller keyed accounts and signer set |
| programs/bpf_loader/src/syscalls.rs | 742 | invokes verification after translating instruction and signer seeds and before message dispatch |
| runtime/src/message_processor.rs | 123 | changes previous cross-program account verification/update behavior in the runtime message processor |
| programs/bpf_loader/src/lib.rs | 184 | passes parameter accounts into BPF VM creation, keeping loader execution context aligned with account privileges |

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

Add a pre-dispatch privilege validation gate at the BPF CPI syscall boundary.

## How It Was Fixed

The patch adds verify_instruction in programs/bpf_loader/src/syscalls.rs and calls it after instruction and signer translation but before Message::new_with_payer and downstream invocation. Supporting changes pass parameter_accounts into BPF VM creation and adjust runtime PreAccount cross-program verification/update handling, but those are not independently proven as the vulnerability root cause from the supplied snippets.

# Why It Matters

1. Preserves caller-to-callee CPI privilege boundaries.

2. Blocks unauthorized writable or signer privilege escalation before dispatch.

3. Places validation at the syscall boundary where untrusted BPF input is translated.

4. Evidence supports a security fix, but not a complete exploit reconstruction.

# Evidence Notes

Primary evidence: programs/bpf_loader/src/syscalls.rs adds verify_instruction with changed lines showing a privilege-escalation check over instruction accounts and caller keyed accounts, then calls it before Message::new_with_payer. The commit subject also states "Prevent privilege escalation (#10232)". The runtime/src/message_processor.rs and programs/bpf_loader/src/lib.rs snippets are relevant support, but do not prove storage corruption or a separate root cause. Protocol security invariant: A BPF program making a cross-program invocation must not grant an invoked instruction account privileges beyond those available to the caller, including writable or signer authority, except where signer authority is represented in the translated signer set. Verification notes: The patch evidence does not prove a complete end-to-end exploit transaction. The evidence does not show which specific account privilege combinations were exploitable beyond signer/writable escalation checks. The patch does not prove corruption of persistent account storage as the primary bug shape. The analysis is limited to the provided diff context and does not rely on external Solana history. No external context was used. No complete exploit transaction is shown in the supplied evidence. Specific failing privilege combinations are not fully visible from the snippets. The security classification rests on the commit subject plus the explicit added privilege-check path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `missing-privilege-check`
Final impact type: `privilege-escalation, state-integrity`
Final tags: `blockchain-core, bpf-loader, cross-program-invocation, privilege-escalation, access-control`

The supplied evidence supports retaining this as a security fix, but not with the original storage/state-corruption framing. The commit subject explicitly says it prevents privilege escalation, and the patch adds a verify_instruction helper in the BPF cross-program invocation syscall path with an explicit privilege-escalation check before dispatch. The strongest supported finding is a missing privilege validation gate for signer/writable authority in CPI, not a storage, queue, or snapshot issue.

## Security Evidence

1. Commit subject is "Prevent privilege escalation (#10232)".
2. programs/bpf_loader/src/syscalls.rs adds verify_instruction before CPI dispatch.
3. New helper comment explicitly says "Check for privilege escalation".
4. The helper examines caller keyed accounts against invoked instruction accounts and signer data.
5. The call path now translates signer seeds and calls verify_instruction before Message construction and dispatch.

## Missing Evidence

1. No complete exploit transaction or proof-of-exploit path is shown.
2. The exact failing signer/writable account combinations are only partially visible in the snippets.
3. The evidence does not support the original storage, queue, or snapshot tags.
4. The evidence does not prove persistent storage corruption as the primary impact.

## Claim Boundaries

1. Validate as a BPF CPI privilege-check security fix.
2. Do not claim a storage subsystem vulnerability from the supplied evidence.
3. Do not claim queue or snapshot involvement.
4. Do not claim a complete exploit reconstruction beyond unauthorized signer/writable privilege escalation prevention.
