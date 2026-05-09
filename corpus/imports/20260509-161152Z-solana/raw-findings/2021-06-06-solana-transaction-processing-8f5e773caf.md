---
case_id: case_20210606_8f5e773caf
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2021-06-06
source_refs:
  - git:8f5e773caf41edc30f26a48cca5b4b1ffedf0a8d
  - "transaction-status/src/parse_stake.rs:310"
  - "runtime/src/system_instruction_processor.rs:1109"
  - "runtime/src/system_instruction_processor.rs:887"
  - "runtime/src/system_instruction_processor.rs:201"
bug_class: missing-authorization
impact_type:
  - unauthorized-instruction-acceptance
tags:
  - blockchain-core
  - transaction-processing
  - signature-check
  - zero-lamport-transfer
  - authorization-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded security-relevant change is in the system-program transfer handler. Previously, `transfer` returned `Ok(())` immediately for `lamports == 0`, before checking whether the source account had signed. The patch feature-gates that legacy fast path so that, once `system_transfer_zero_check` is active, zero-lamport transfers continue to the existing missing-signature check. This supports a missing-authorization hardening finding, but the evidence does not establish lamport theft, balance corruption, or a full exploit chain.

## Observed Patch Facts

1. In `transaction-status/src/parse_stake.rs`, the patch replaces `let instructions = stake_instruction::split(&keys[2], &keys[0], lamports, &keys[1]);` with `// This looks wrong, but in an actual compiled instruction, the order is:`.

2. In `runtime/src/system_instruction_processor.rs`, the patch adds `// test unsigned transfer of zero`.

3. In `runtime/src/system_instruction_processor.rs`, the patch replaces `assert_eq!(result, Ok(()));` with `assert_eq!(result, Err(InstructionError::MissingRequiredSignature));`.

4. In `runtime/src/system_instruction_processor.rs`, the patch replaces `if lamports == 0 {` with `if !invoke_context.is_feature_active(&feature_set::system_transfer_zero_check::id())`.

## Project Context

The changed code sits primarily in `transaction-status/src`, `runtime/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `transaction-status/src/parse_vote.rs`, `transaction-status/src/parse_system.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `transaction-status/src/parse_vote.rs`, `transaction-status/src/parse_system.rs`. The strongest project-level identifiers around this patch are `keys`, `stake_instruction::split`, `lamports`, and `instructions`.

## Before/After Behavior

Before the patch, an unsigned zero-lamport transfer could be accepted because the handler returned success before source-signer validation. After the patch, that early return applies only while `system_transfer_zero_check` is inactive; with the feature active, zero-lamport transfers reach signer validation and unsigned attempts return `InstructionError::MissingRequiredSignature`. Adjacent stake parser test changes concern split instruction account ordering and should not be treated as the root security issue.

# Root Cause

A zero-value special case was placed before authorization validation in the transfer control flow, allowing the handler to accept a zero-lamport transfer without evaluating whether the source account was a signer.

## Walkthrough

1. A system-program transfer enters `runtime/src/system_instruction_processor.rs::transfer` with `lamports == 0`.

2. Old behavior returned `Ok(())` immediately for that amount.

3. That return happened before the `from.signer_key().is_none()` missing-signature check.

4. The patch changes the early return to apply only when `system_transfer_zero_check` is inactive.

5. With the feature active, zero-lamport transfers follow the same signer-validation path as nonzero transfers.

6. Tests were updated so unsigned zero-lamport transfer cases expect `InstructionError::MissingRequiredSignature`.

7. Stake parser test changes are adjacent correctness work, not evidence for this authorization issue.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/system_instruction_processor.rs | 197 | system-program transfer handler; feature-gates the old zero-lamport early return so active behavior enforces signer authorization |
| runtime/src/system_instruction_processor.rs | 887 | regression test expectation changed from accepting an unsigned zero-lamport operation to MissingRequiredSignature |
| runtime/src/system_instruction_processor.rs | 1109 | adds explicit coverage that unsigned transfer of zero lamports fails |
| transaction-status/src/parse_stake.rs | 310 | stake instruction parser test adjustment for split instruction account ordering; adjacent correctness change rather than primary authorization guard |

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

Do not let no-op or zero-value fast paths bypass authorization checks. Gate legacy behavior where needed and route active behavior through the same validation path as normal state-changing operations.

## How It Was Fixed

The unconditional `lamports == 0` success return in `transfer` was changed to a feature-gated legacy branch using `system_transfer_zero_check`. Tests were updated to assert that unsigned zero-lamport transfer attempts fail with `MissingRequiredSignature`.

# Why It Matters

1. Maintains a consistent signer requirement for system-program transfers.

2. Removes an unauthenticated success path for zero-lamport transfers when the feature is active.

3. Reduces ambiguity between accepted no-op instructions and authorized transfer instructions.

4. Impact beyond unauthorized acceptance is not proven by the provided evidence.

# Evidence Notes

Strong direct evidence exists for the behavior change in `runtime/src/system_instruction_processor.rs`: the zero-lamport early return was changed from unconditional to feature-gated, and tests changed from accepting unsigned zero-lamport behavior to expecting `InstructionError::MissingRequiredSignature`. The evidence supports missing authorization on an accepted zero-value transfer path. It does not support stronger claims such as theft, balance corruption, stake-account compromise, or parser-driven vulnerability. Behavior depends on activation of `system_transfer_zero_check`. Protocol security invariant: System-program transfer instructions should not be accepted without the required source-account signer authorization, including when the requested lamport amount is zero. Verification notes: The patch does not prove lamports could be stolen or balances directly changed by the old zero-lamport path. The patch does not show a complete exploit chain using unsigned zero-lamport transfers. The transaction-status parser changes do not by themselves establish a security issue. The feature gate means behavior depends on activation of `system_transfer_zero_check`. Confirmed by provided diff snippets only; no external inspection used. Primary evidence is the `transfer` control-flow change around line 197. Regression evidence is the changed and added tests around lines 887 and 1109. Stake parser changes should be excluded from the root-cause claim. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-authorization`
Final impact type: `unauthorized-instruction-acceptance`
Final tags: `blockchain-core, transaction-processing, signature-check, zero-lamport-transfer, authorization-hardening`

The supplied patch evidence supports a security-hardening finding, not the stronger original state-corruption framing. The transfer handler previously returned success for zero-lamport transfers before signer validation; the patch feature-gates that legacy fast path so active behavior reaches the missing-signature check, and tests now expect unsigned zero-lamport transfers to fail. The evidence shows authorization tightening on a security-sensitive runtime path, but not theft, balance corruption, or a complete exploit chain.

## Security Evidence

1. `transfer` changed the unconditional `lamports == 0` early `Ok(())` return into a feature-gated legacy branch.
2. With `system_transfer_zero_check` active, zero-lamport transfers proceed to `from.signer_key().is_none()` validation.
3. A test expectation changed from `Ok(())` to `Err(InstructionError::MissingRequiredSignature)` for the affected behavior.
4. Additional test coverage explicitly checks unsigned transfer of zero lamports.

## Missing Evidence

1. No evidence that nonzero lamports could be moved without authorization.
2. No evidence of balance corruption, state corruption, or stake-account compromise.
3. No full exploit chain or external attacker impact is shown.
4. Stake parser changes appear adjacent and do not establish the security issue.

## Claim Boundaries

1. Validate only as authorization hardening for zero-lamport system transfers.
2. Do not claim lamport theft or direct state corruption from the provided evidence.
3. Behavior depends on activation of `system_transfer_zero_check`.
4. Do not use the stake parser test adjustment as primary security evidence.
