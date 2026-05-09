---
case_id: case_20210607_b777bbf7db
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: medium
date: 2021-06-07
source_refs:
  - git:b777bbf7db326a8c943c6aa65acca4096b2fae74
  - "transaction-status/src/parse_stake.rs:310"
  - "runtime/src/system_instruction_processor.rs:1102"
  - "runtime/src/system_instruction_processor.rs:880"
  - "runtime/src/system_instruction_processor.rs:201"
bug_class: missing-authorization-check
impact_type:
  - authorization-bypass
confidence: high
tags:
  - blockchain-core
  - transaction-processing
  - authorization
  - signature-validation
  - zero-value-transfer
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is limited to authorization hardening in Solana's runtime system-program transfer path. Before the patch, `transfer` returned `Ok(())` immediately for `lamports == 0`, before checking whether the source account signed. After the patch, that early return is feature-gated, so once `system_transfer_zero_check` is active, zero-lamport transfers enter the normal signer-validation path and unsigned transfers fail with `InstructionError::MissingRequiredSignature`. The evidence does not establish lamport theft, state corruption, or a complete exploit path.

## Observed Patch Facts

1. In `transaction-status/src/parse_stake.rs`, the patch replaces `let instructions = stake_instruction::split(&keys[2], &keys[0], lamports, &keys[1]);` with `// This looks wrong, but in an actual compiled instruction, the order is:`.

2. In `runtime/src/system_instruction_processor.rs`, the patch adds `// test unsigned transfer of zero`.

3. In `runtime/src/system_instruction_processor.rs`, the patch replaces `assert_eq!(result, Ok(()));` with `assert_eq!(result, Err(InstructionError::MissingRequiredSignature));`.

4. In `runtime/src/system_instruction_processor.rs`, the patch replaces `if lamports == 0 {` with `if !invoke_context.is_feature_active(&feature_set::system_transfer_zero_check::id())`.

## Project Context

The changed code sits primarily in `transaction-status/src`, `runtime/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `transaction-status/src/parse_vote.rs`, `transaction-status/src/parse_system.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `transaction-status/src/parse_vote.rs`, `transaction-status/src/parse_system.rs`. The strongest project-level identifiers around this patch are `keys`, `stake_instruction::split`, `lamports`, and `instructions`.

## Before/After Behavior

Before, zero-lamport transfers could succeed through an unconditional early return before source-account signer validation. After, the early return applies only while `system_transfer_zero_check` is inactive; with the feature active, zero-lamport transfers fall through to the same missing-signature check as nonzero transfers. Tests were updated to expect `MissingRequiredSignature` for unsigned zero-lamport transfer/create-account paths. The stake parser/test changes are account-ordering compatibility work and are not evidence of the security issue.

# Root Cause

A value-based fast path in `runtime/src/system_instruction_processor.rs::transfer` treated zero-lamport transfers as immediate success before evaluating the source-account signature requirement. That allowed unsigned zero-value transfer operations to avoid the normal authorization failure.

## Walkthrough

1. The original `transfer` implementation had an early `if lamports == 0 { return Ok(()); }` branch.

2. The source signer check occurred after that branch, so zero-lamport transfers did not necessarily evaluate `from.signer_key().is_none()`.

3. The patch changed the branch to return early only when `system_transfer_zero_check` is not active and `lamports == 0`.

4. With the feature active, zero-lamport transfers continue into the normal signer-validation logic.

5. Regression tests now expect unsigned zero-lamport transfer behavior to return `InstructionError::MissingRequiredSignature`.

6. A create-account test involving zero lamports was also updated to expect missing-signature failure.

7. The stake split parser/test updates concern instruction account ordering and should be treated as related compatibility changes, not the vulnerability root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/system_instruction_processor.rs | 197 | system transfer authorization path; moves zero-lamport behavior behind feature activation so signer validation can run |
| runtime/src/system_instruction_processor.rs | 880 | regression test expectation changed from unsigned zero-lamport account creation succeeding to missing signature failure |
| runtime/src/system_instruction_processor.rs | 1102 | regression coverage for unsigned zero-lamport transfer returning MissingRequiredSignature |
| transaction-status/src/parse_stake.rs | 310 | stake split parser/test account-order update related to changed split instruction construction, not the primary authorization invariant |

## Code Snippets

## Snippet 1

Context: `transaction-status/src/parse_stake.rs:310` (changes the branch that decides whether execution stops or continues)

Before
```rust
assert!(parse_stake(&message.instructions[0], &keys[0..5]).is_err());

        let instructions = stake_instruction::split(&keys[2], &keys[0], lamports, &keys[1]);
        let message = Message::new(&instructions, None);
        assert_eq!(
            parse_stake(&message.instructions[1], &keys[0..3]).unwrap(),
            ParsedInstructionEnum {
                instruction_type: "split".to_string(),
```
After
```rust
assert!(parse_stake(&message.instructions[0], &keys[0..5]).is_err());

        // This looks wrong, but in an actual compiled instruction, the order is:
        //  * split account (signer, allocate + assign first)
        //  * stake authority (signer)
        //  * stake account
        let instructions = stake_instruction::split(&keys[2], &keys[1], lamports, &keys[0]);
        let message = Message::new(&instructions, None);
```

## Snippet 2

Context: `runtime/src/system_instruction_processor.rs:1102` (changes the branch that decides whether execution stops or continues)

Before
```rust
assert_eq!(from_keyed_account.account.borrow().lamports, 50);
        assert_eq!(to_keyed_account.account.borrow().lamports, 51);
    }
```
After
```rust
assert_eq!(from_keyed_account.account.borrow().lamports, 50);
        assert_eq!(to_keyed_account.account.borrow().lamports, 51);

        // test unsigned transfer of zero
        let from_keyed_account = KeyedAccount::new(&from, false, &from_account);

        assert_eq!(
            transfer(
```

## Snippet 3

Context: `runtime/src/system_instruction_processor.rs:880` (changes the branch that decides whether execution stops or continues)

Before
```rust
&mut MockInvokeContext::default(),
        );
        assert_eq!(result, Ok(()));
    }
```
After
```rust
&mut MockInvokeContext::default(),
        );
        assert_eq!(result, Err(InstructionError::MissingRequiredSignature));
    }
```

## Snippet 4

Context: `runtime/src/system_instruction_processor.rs:201` (changes a sensitive control or state-update path)

Before
```rust
invoke_context: &mut dyn InvokeContext,
) -> Result<(), InstructionError> {
    if lamports == 0 {
        return Ok(());
    }
```
After
```rust
invoke_context: &mut dyn InvokeContext,
) -> Result<(), InstructionError> {
    if !invoke_context.is_feature_active(&feature_set::system_transfer_zero_check::id())
        && lamports == 0
    {
        return Ok(());
    }
```

# Fix Pattern

Gate or remove zero-value fast paths that bypass authorization so no-op amounts still pass through the same signature validation required for the instruction type.

## How It Was Fixed

The `transfer` helper was changed so the zero-lamport early success path is disabled after activation of `feature_set::system_transfer_zero_check`. Tests were added or updated to assert that unsigned zero-lamport transfer and creation paths fail with `InstructionError::MissingRequiredSignature`.

# Why It Matters

1. Maintains a consistent authorization rule for system transfers regardless of amount.

2. Prevents zero-value transfer instructions from bypassing required signature validation.

3. Reduces ambiguity around unsigned system-program operations.

4. Evidence supports authorization hardening, not proven asset loss or state corruption.

# Evidence Notes

The strongest evidence is the change in `runtime/src/system_instruction_processor.rs::transfer` from unconditional zero-lamport success to a feature-gated early return, plus tests expecting `MissingRequiredSignature` for unsigned zero-lamport behavior. The provided evidence does not support the stronger heuristic claim of state corruption, nor does it prove theft or a full exploit chain. `transaction-status/src/parse_stake.rs` changes are parser/test ordering adjustments and should not be used as the main security basis. Protocol security invariant: System-program transfer handling should enforce the source-account signature requirement even when the transfer amount is zero lamports; a zero-value fast path should not bypass authorization checks for the same instruction path. Verification notes: The patch does not show theft or movement of lamports without authorization. The patch does not prove a full exploit path using zero-lamport transfers. The transaction-status parser changes do not themselves establish a security bug. The evidence supports an authorization hardening/fix, not a broader state-corruption claim. Runtime transfer code shows signer validation can run for zero-lamport transfers after feature activation. Tests explicitly cover unsigned zero-lamport transfer returning `MissingRequiredSignature`. Create-account zero-lamport unsigned behavior is covered by changed test expectation. No supplied evidence demonstrates lamport movement without authorization or broader state corruption. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-authorization-check`
Final impact type: `authorization-bypass`
Final confidence: `high`
Final tags: `blockchain-core, transaction-processing, authorization, signature-validation, zero-value-transfer`

The supplied patch evidence clearly shows a zero-lamport transfer fast path previously returned success before signer validation, and the change makes that bypass conditional on a feature flag so active behavior falls through to the missing-signature check. Updated tests explicitly expect unsigned zero-lamport transfer and create-account behavior to fail with MissingRequiredSignature. This supports security hardening of authorization enforcement, but not the stronger original state-corruption framing or a proven exploit with asset loss.

## Security Evidence

1. runtime transfer changed from unconditional lamports == 0 success to feature-gated early return
2. transfer path now reaches from.signer_key() validation for zero-lamport transfers when system_transfer_zero_check is active
3. tests changed from Ok(()) to MissingRequiredSignature for unsigned zero-lamport account creation
4. new test coverage expects unsigned zero-lamport transfer to return MissingRequiredSignature
5. changed code is in the system-program runtime transfer path, a security-sensitive authorization path

## Missing Evidence

1. No evidence of lamport theft or unauthorized value movement
2. No full exploit path is shown
3. No evidence supports state corruption as the bug class
4. Stake parser/order changes appear compatibility-related rather than security-relevant

## Claim Boundaries

1. Validate only as authorization hardening for zero-lamport system-program operations
2. Do not claim asset loss, state corruption, or consensus compromise from the provided patch alone
3. Do not use transaction-status stake parser changes as primary security evidence
4. Feature-gated behavior means the validated claim is limited to behavior after system_transfer_zero_check activation
