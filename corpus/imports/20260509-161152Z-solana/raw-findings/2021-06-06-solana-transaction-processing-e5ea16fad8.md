---
case_id: case_20210606_e5ea16fad8
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: medium
date: 2021-06-06
source_refs:
  - git:e5ea16fad840b12c62ae36e7dd1287552ee63f12
  - "transaction-status/src/parse_stake.rs:310"
  - "runtime/src/system_instruction_processor.rs:1109"
  - "runtime/src/system_instruction_processor.rs:887"
  - "runtime/src/system_instruction_processor.rs:201"
bug_class: authorization-check-bypass
impact_type:
  - authorization-bypass
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - system-program
  - authorization
  - signature-check
  - zero-value-transfer
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is limited to an authorization check gap in zero-lamport System Program transfers. Before the patch, `transfer` returned `Ok(())` for `lamports == 0` before checking whether the source account signed. After the patch, that legacy early return is gated behind `!system_transfer_zero_check`, so when the feature is active the existing missing-signature check runs and unsigned zero-lamport transfers fail.

## Observed Patch Facts

1. In `transaction-status/src/parse_stake.rs`, the patch replaces `let instructions = stake_instruction::split(&keys[2], &keys[0], lamports, &keys[1]);` with `// This looks wrong, but in an actual compiled instruction, the order is:`.

2. In `runtime/src/system_instruction_processor.rs`, the patch adds `// test unsigned transfer of zero`.

3. In `runtime/src/system_instruction_processor.rs`, the patch replaces `assert_eq!(result, Ok(()));` with `assert_eq!(result, Err(InstructionError::MissingRequiredSignature));`.

4. In `runtime/src/system_instruction_processor.rs`, the patch replaces `if lamports == 0 {` with `if !invoke_context.is_feature_active(&feature_set::system_transfer_zero_check::id())`.

## Project Context

The changed code sits primarily in `transaction-status/src`, `runtime/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `transaction-status/src/parse_vote.rs`, `transaction-status/src/parse_system.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `transaction-status/src/parse_vote.rs`, `transaction-status/src/parse_system.rs`. The strongest project-level identifiers around this patch are `keys`, `stake_instruction::split`, `lamports`, and `instructions`.

## Before/After Behavior

Before the patch, zero-lamport transfers could return success before `from.signer_key()` was checked. After the patch, zero-lamport transfers only keep that early-success behavior while the feature is inactive; with `system_transfer_zero_check` active, unsigned zero-lamport transfers return `InstructionError::MissingRequiredSignature`. Tests were updated from expecting success to expecting `MissingRequiredSignature`, and explicit unsigned zero-transfer coverage was added. The stake parser updates are related commit work but are not supported as the root security issue.

# Root Cause

A zero-value fast path in the System Program transfer handler was placed before source-account authorization, allowing the zero-lamport case to skip the signer requirement enforced for nonzero transfers.

## Walkthrough

1. A System Program transfer enters `transfer(from, to, lamports, invoke_context)`.

2. Old behavior checked `lamports == 0` first and returned `Ok(())`.

3. That early return prevented the later `from.signer_key().is_none()` check from running for zero-lamport transfers.

4. The tests show this behavior changing from success to `InstructionError::MissingRequiredSignature` for an unsigned zero-lamport path.

5. The patch gates the early return on the `system_transfer_zero_check` feature being inactive.

6. With the feature active, zero-lamport transfers proceed to the existing source-signature validation.

7. Unsigned zero-lamport transfers now fail with `MissingRequiredSignature`.

8. Stake split parser/test changes adjust account ordering and are not evidence of a separate vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/system_instruction_processor.rs | 201 | System Program transfer handler; zero-lamport early return is gated so signature validation can run. |
| runtime/src/system_instruction_processor.rs | 887 | Regression test expectation changed from unsigned zero-lamport create/transfer success to missing signature. |
| runtime/src/system_instruction_processor.rs | 1109 | Regression coverage added for unsigned zero-lamport transfer returning `MissingRequiredSignature`. |
| transaction-status/src/parse_stake.rs | 310 | Stake split parser/test account ordering update related to split instruction sequence, not the core authorization check. |

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

Context: `runtime/src/system_instruction_processor.rs:1109` (changes the branch that decides whether execution stops or continues)

Before
```rust
assert_eq!(from_keyed_account.account.borrow().lamports(), 50);
        assert_eq!(to_keyed_account.account.borrow().lamports(), 51);
    }
```
After
```rust
assert_eq!(from_keyed_account.account.borrow().lamports(), 50);
        assert_eq!(to_keyed_account.account.borrow().lamports(), 51);

        // test unsigned transfer of zero
        let from_keyed_account = KeyedAccount::new(&from, false, &from_account);

        assert_eq!(
            transfer(
```

## Snippet 3

Context: `runtime/src/system_instruction_processor.rs:887` (changes the branch that decides whether execution stops or continues)

Before
```rust
&MockInvokeContext::new(vec![]),
        );
        assert_eq!(result, Ok(()));
    }
```
After
```rust
&MockInvokeContext::new(vec![]),
        );
        assert_eq!(result, Err(InstructionError::MissingRequiredSignature));
    }
```

## Snippet 4

Context: `runtime/src/system_instruction_processor.rs:201` (changes a sensitive control or state-update path)

Before
```rust
invoke_context: &dyn InvokeContext,
) -> Result<(), InstructionError> {
    if lamports == 0 {
        return Ok(());
    }
```
After
```rust
invoke_context: &dyn InvokeContext,
) -> Result<(), InstructionError> {
    if !invoke_context.is_feature_active(&feature_set::system_transfer_zero_check::id())
        && lamports == 0
    {
        return Ok(());
    }
```

# Fix Pattern

Gate or remove special-case zero-value fast paths so authorization checks still execute before success is returned.

## How It Was Fixed

The unconditional `lamports == 0` early return was changed to apply only when `system_transfer_zero_check` is inactive. Once the feature is active, zero-lamport transfers follow the normal transfer validation path and require the source account signature. Regression tests were updated to assert `MissingRequiredSignature` for unsigned zero-lamport behavior.

# Why It Matters

1. Keeps signer enforcement consistent across zero and nonzero transfers.

2. Prevents zero-value System Program transfers from being accepted before authorization runs.

3. Evidence supports an authorization hardening claim, not lamport theft or balance corruption.

# Evidence Notes

Primary evidence is the `runtime/src/system_instruction_processor.rs::transfer` hunk changing `if lamports == 0 { return Ok(()); }` to a feature-gated early return. Test evidence shows expectations changing from `Ok(())` to `Err(InstructionError::MissingRequiredSignature)` and adds explicit unsigned zero-lamport transfer coverage. The provided stake parser evidence concerns instruction account ordering and should be treated as supporting or unrelated commit work, not the root cause. Protocol security invariant: System Program transfers should not bypass source-account signature validation solely because the requested lamport amount is zero. Verification notes: No lamport theft or balance-changing exploit is proven by the patch evidence. No remote exploit path is shown beyond acceptance of an unsigned zero-value transfer instruction. Stake parser changes do not by themselves show a security invariant violation. The evidence supports an authorization hardening/fix, but not broader state-corruption claims. Supported by runtime transfer handler diff. Supported by updated missing-signature regression tests. No evidence proves balance theft, state corruption, or a broader exploit path. No evidence supports treating helper or parser changes as the root vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `authorization-check-bypass`
Final impact type: `authorization-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, system-program, authorization, signature-check, zero-value-transfer`

The supplied patch evidence clearly shows a security-sensitive authorization behavior being tightened: zero-lamport System Program transfers previously returned success before the signer check, and the patched behavior makes unsigned zero-lamport transfers fail once the feature is active. This supports retaining the case as security hardening, but the original state-corruption framing is too strong because no balance change, theft, or concrete exploit path is proven by the patch alone.

## Security Evidence

1. The transfer handler changed an unconditional `lamports == 0` early return into a feature-gated legacy path.
2. The shown post-patch control flow reaches `from.signer_key().is_none()` when `system_transfer_zero_check` is active.
3. A test expectation changed from `Ok(())` to `Err(InstructionError::MissingRequiredSignature)` for a zero-lamport unsigned path.
4. Additional test coverage explicitly checks unsigned transfer of zero returns `MissingRequiredSignature`.

## Missing Evidence

1. No evidence shows lamport theft or unauthorized balance mutation.
2. No evidence shows a concrete remote exploit chain beyond acceptance of an unsigned zero-value instruction.
3. No evidence supports state corruption as the primary bug class.
4. Stake parser changes appear related to account ordering and do not establish a separate security issue.

## Claim Boundaries

1. Validate only as authorization hardening for zero-lamport System Program transfers.
2. Do not claim nonzero transfers were affected.
3. Do not claim balance theft, fund loss, or state corruption from the supplied evidence.
4. Treat the stake split parser changes as unrelated or ancillary unless further evidence is supplied.
