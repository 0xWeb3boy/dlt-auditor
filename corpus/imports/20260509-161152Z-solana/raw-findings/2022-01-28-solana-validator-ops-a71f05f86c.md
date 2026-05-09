---
case_id: case_20220128_a71f05f86c
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: validator-ops
confidence: high
source_quality: medium
date: 2022-01-28
source_refs:
  - git:a71f05f86c7ccc170f376f67f2227b8c3dc49880
  - "program-runtime/src/invoke_context.rs:699"
  - "program-runtime/src/invoke_context.rs:708"
  - "programs/bpf/rust/invoke/src/processor.rs:638"
  - "programs/bpf/c/src/invoke/invoke.c:614"
bug_class: cpi-duplicate-account-privilege-escalation
impact_type:
  - privilege-escalation
  - authorization-bypass
tags:
  - blockchain-core
  - cpi
  - duplicate-account
  - privilege-escalation
  - writable-account-escalation
  - regression-test
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes CPI duplicate account privilege handling in Solana's instruction preparation path. Duplicate account metas are normalized by merging privilege bits, so privilege checks must be applied after deduplication to the final effective account entry. The supplied implementation evidence directly shows writable privilege validation moved from inside the deduplication loop to a post-deduplication pass; signer coverage is supported by the commit message and added regression test names, but the signer validation hunk itself is not included.

## Observed Patch Facts

1. In `program-runtime/src/invoke_context.rs`, the patch replaces `let borrowed_account = instruction_context` with `duplicate_indicies.push(deduplicated_instruction_accounts.len());`.

2. In `program-runtime/src/invoke_context.rs`, the patch replaces `let instruction_accounts: Vec<InstructionAccount> = duplicate_indicies` with `for instruction_account in deduplicated_instruction_accounts.iter() {`.

3. In `programs/bpf/rust/invoke/src/processor.rs`, the patch replaces `_ => panic!(),` with `TEST_DUPLICATE_PRIVILEGE_ESCALATION_SIGNER => {`.

4. In `programs/bpf/c/src/invoke/invoke.c`, the patch replaces `default:` with `case TEST_DUPLICATE_PRIVILEGE_ESCALATION_SIGNER: {`.

## Project Context

The changed code sits primarily in `program-runtime/src`, `programs/bpf/rust/invoke/src`, `programs/bpf/rust/invoke`, which anchors the finding in the `validator-ops` area of the project. Historical context from `program-runtime/src/accounts_data_meter.rs`, `programs/bpf/rust/invoke/src/instructions.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `programs/bpf/c/src/invoked/invoked.c`, `programs/bpf/rust/invoke/src/instructions.rs`. The strongest project-level identifiers around this patch are `accounts`, `borrowed_account`, `InstructionError::MissingAccount`, and `is_writable`.

## Before/After Behavior

Before the patch, writable privilege validation was performed while processing an individual non-duplicate account meta inside the deduplication loop. A later duplicate meta could then merge additional privilege bits into the existing deduplicated instruction account after that check point. After the patch, the function first builds and merges `deduplicated_instruction_accounts`, then iterates over those final entries and validates their effective privileges against the caller account context before continuing.

# Root Cause

Privilege validation occurred too early relative to duplicate account normalization. Because duplicate metas can update an existing deduplicated `InstructionAccount` by ORing privilege bits such as `is_writable`, the final effective privileges could differ from the state that had already been checked.

## Walkthrough

1. `prepare_instruction` receives CPI account metas and maps them to transaction and caller account indexes.

2. Repeated account metas are deduplicated by transaction account index.

3. When a duplicate is found, the existing deduplicated account has privilege bits merged into it.

4. Before the fix, the shown readonly-to-writable check ran while processing an individual new account entry, before all duplicate privilege bits were necessarily merged.

5. The fix completes deduplication first, then borrows each caller account and checks the final effective writable privilege against the caller context.

6. Regression paths were added in Rust and C BPF invoke programs for duplicate privilege escalation cases; signer-specific behavior is evidenced by names and commit text, not by the supplied implementation hunk.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| program-runtime/src/invoke_context.rs | 656 | CPI instruction preparation deduplicates account metas and merges duplicate account privileges. |
| program-runtime/src/invoke_context.rs | 708 | Post-deduplication privilege validation checks effective writable and signer privileges against caller context. |
| programs/bpf/rust/invoke/src/processor.rs | 638 | Rust BPF regression path constructs duplicate account metas for privilege escalation coverage. |
| programs/bpf/c/src/invoke/invoke.c | 614 | C BPF regression path constructs duplicate account metas for privilege escalation coverage. |

## Code Snippets

## Snippet 1

Context: `program-runtime/src/invoke_context.rs:699` (changes a sensitive control or state-update path)

Before
```rust
InstructionError::MissingAccount
                    })?;
                let borrowed_account = instruction_context
                    .try_borrow_account(self.transaction_context, index_in_caller)?;

                // Readonly in caller cannot become writable in callee
                if account_meta.is_writable && !borrowed_account.is_writable() {
                    ic_msg!(
```
After
```rust
InstructionError::MissingAccount
                    })?;
                duplicate_indicies.push(deduplicated_instruction_accounts.len());
                deduplicated_instruction_accounts.push(InstructionAccount {
```

## Snippet 2

Context: `program-runtime/src/invoke_context.rs:708` (changes a sensitive control or state-update path)

Before
```rust
}
        }
        let instruction_accounts: Vec<InstructionAccount> = duplicate_indicies
            .into_iter()
```
After
```rust
}
        }
        for instruction_account in deduplicated_instruction_accounts.iter() {
            let borrowed_account = instruction_context.try_borrow_account(
                self.transaction_context,
                instruction_account.index_in_caller,
            )?;
```

## Snippet 3

Context: `programs/bpf/rust/invoke/src/processor.rs:638` (changes a sensitive control or state-update path)

Before
```rust
set_return_data(&[1u8; 1028]);
        }
        _ => panic!(),
    }
```
After
```rust
set_return_data(&[1u8; 1028]);
        }
        TEST_DUPLICATE_PRIVILEGE_ESCALATION_SIGNER => {
            msg!("Test duplicate privilege escalation signer");
            let mut invoked_instruction = create_instruction(
                *accounts[INVOKED_PROGRAM_INDEX].key,
                &[
                    (accounts[DERIVED_KEY3_INDEX].key, false, false),
```

## Snippet 4

Context: `programs/bpf/c/src/invoke/invoke.c:614` (changes a sensitive control or state-update path)

Before
```c
break;
  }

  default:
```
After
```c
break;
  }
  case TEST_DUPLICATE_PRIVILEGE_ESCALATION_SIGNER: {
    sol_log("Test duplicate privilege escalation signer");
    SolAccountMeta arguments[] = {
        {accounts[DERIVED_KEY3_INDEX].key, false, false},
        {accounts[DERIVED_KEY3_INDEX].key, false, false},
        {accounts[DERIVED_KEY3_INDEX].key, false, false}};
```

# Fix Pattern

Normalize duplicate account references first, compute the final effective privilege set, then enforce CPI privilege invariants against that normalized state.

## How It Was Fixed

The writable privilege check was moved out of the per-meta deduplication loop and into a later pass over `deduplicated_instruction_accounts`. The later pass borrows the corresponding caller account and rejects an instruction account whose final effective writable flag exceeds the caller account's writable permission. The commit also adds duplicate privilege escalation regression cases in Rust and C BPF invoke test programs.

# Why It Matters

1. CPI must preserve caller-imposed account privilege limits.

2. Duplicate account metas can change the effective privilege set after merging.

3. Checking privileges before deduplication is complete can miss the final privilege state.

4. The evidence supports a CPI privilege escalation fix, not memory corruption or arbitrary asset theft.

# Evidence Notes

Primary evidence is in `program-runtime/src/invoke_context.rs::prepare_instruction`, where the writable privilege check is removed from the deduplication loop and reintroduced after deduplicated accounts are built. The commit subject and body explicitly identify duplicate CPI privilege escalation and mention signer and writable regression tests. The supplied test hunks show added duplicate signer test paths in Rust and C. The exact signer validation implementation hunk is not present, so signer behavior should be treated as supported by commit/test evidence rather than directly shown in the provided code excerpt. Protocol security invariant: During cross-program invocation, the callee must not receive account privileges that exceed the caller context. In particular, a readonly caller account must not become writable, and signer privileges must not be introduced through duplicate account metadata after normalization. Verification notes: The patch does not prove arbitrary account takeover or asset theft by itself. The evidence is limited to CPI duplicate account privilege handling, not general validator operation correctness. No memory-safety issue is shown. The exact signer-side validation hunk is inferred from the commit message and tests, while the provided implementation excerpt directly shows writable validation. The patch demonstrates a security invariant fix, but not the full exploit preconditions or impact in deployed clusters. Directly verified from supplied evidence: writable privilege validation moved after deduplication. Directly verified from supplied evidence: duplicate account metas merge privilege bits into existing deduplicated entries. Supported by commit/test evidence: duplicate signer privilege escalation regression coverage was added. Not established by supplied evidence: arbitrary account takeover, asset theft, memory safety impact, or broader validator correctness claims. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `cpi-duplicate-account-privilege-escalation`
Final impact type: `privilege-escalation, authorization-bypass`
Final tags: `blockchain-core, cpi, duplicate-account, privilege-escalation, writable-account-escalation, regression-test`

The supplied evidence supports keeping this as a security fix. The runtime code moved CPI privilege checks from the per-account deduplication loop to a post-deduplication pass over the final effective account privileges, closing a path where duplicate account metas could merge writable or signer privileges after validation. The original state-corruption framing is too broad; the supported issue is CPI duplicate-account privilege escalation / authorization bypass.

## Security Evidence

1. Commit subject explicitly states "Fix CPI duplicate account privilege escalation".
2. Patch shows duplicate account metas are normalized by OR-ing privilege bits into deduplicated instruction accounts.
3. Writable privilege validation was removed from the pre-deduplication loop and reintroduced after deduplication over final instruction accounts.
4. The validation rejects readonly-in-caller becoming writable-in-callee with InstructionError::PrivilegeEscalation.
5. Regression paths were added for duplicate privilege escalation cases in Rust and C BPF invoke programs.

## Missing Evidence

1. The supplied implementation hunks directly show writable validation but not the complete signer validation code.
2. No exploit walkthrough, deployed impact, or asset-loss proof is provided.
3. No evidence supports memory safety, arbitrary account takeover, or broad validator state corruption claims.

## Claim Boundaries

1. Validated scope is CPI duplicate account privilege handling.
2. Directly supported impact is privilege escalation / authorization bypass, especially writable privilege escalation.
3. Signer-related behavior is supported by commit text and test names, but less directly by the shown implementation evidence.
4. Do not generalize this to state corruption, consensus failure, asset theft, or memory corruption from the provided patch alone.
