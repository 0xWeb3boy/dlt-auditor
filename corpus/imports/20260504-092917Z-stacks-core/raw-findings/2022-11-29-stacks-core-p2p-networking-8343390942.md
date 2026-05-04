---
case_id: case_20221129_8343390942
project: stacks-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: p2p-networking
source_quality: high
date: 2022-11-29
source_refs:
  - git:834339094265eb44d7689cfe4fd22ddc146af84f
  - "src/clarity_vm/special.rs:229"
  - "src/clarity_vm/special.rs:685"
  - "src/chainstate/stacks/boot/pox_2_tests.rs:4655"
  - "clarity/src/vm/errors.rs:100"
bug_class: unhandled-protocol-error-panic
impact_type:
  - liveness
confidence: medium
tags:
  - clarity-vm
  - pox
  - error-handling
  - panic-prevention
  - liveness
  - blockchain
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes an unhandled PoX already-locked error in Clarity special contract-call handling. Before the change, `ChainstateError::PoxAlreadyLocked` from PoX v1 or PoX v2 lock application had no dedicated match arm and could fall through to the generic `panic!` branch. After the change, both handlers translate the condition into `Error::Runtime(RuntimeErrorType::PoxAlreadyLocked, None)`, and a regression test covers stacking in both PoX versions.

## Observed Patch Facts

1. In `src/clarity_vm/special.rs`, the patch adds `Err(ChainstateError::PoxAlreadyLocked) => {`.

2. In `src/clarity_vm/special.rs`, the patch adds `Err(ChainstateError::PoxAlreadyLocked) => {`.

3. In `src/chainstate/stacks/boot/pox_2_tests.rs`, the patch adds `#[test]`.

4. In `clarity/src/vm/errors.rs`, the patch adds `PoxAlreadyLocked,`.

## Project Context

The changed code sits primarily in `src/clarity_vm`, `src/chainstate/stacks/boot`, `src/chainstate/stacks`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `clarity/src/vm/mod.rs`, `src/clarity_vm/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `clarity/src/vm/mod.rs`, `src/chainstate/stacks/mod.rs`. The strongest project-level identifiers around this patch are `Error::Runtime`, `RuntimeErrorType::DefunctPoxContract`, `ChainstateError::PoxAlreadyLocked`, and `RuntimeErrorType::PoxAlreadyLocked`. Nearby tests or test-like files include `src/clarity_vm/tests/simple_tests.rs`, `src/clarity_vm/tests/large_contract.rs`.

## Before/After Behavior

Before the patch, `handle_pox_v1_api_contract_call` and `handle_stack_lockup` handled `DefunctPoxContract` specially but not `PoxAlreadyLocked`, so an expected already-locked rejection could reach generic panic handling. After the patch, both paths return a typed Clarity runtime error for `PoxAlreadyLocked`.

# Root Cause

The Clarity VM special PoX handlers had an incomplete error translation boundary. `PoxAlreadyLocked` was an expected chainstate rejection for cross-version lock conflicts, but it was not mapped into a runtime error before the generic panic fallback.

## Walkthrough

1. A PoX v1 or PoX v2 special contract call produces a parsed stacking result.

2. The handler attempts to apply the lock through `pox_lock_v1` or `pox_lock_v2`.

3. The chainstate layer can return `PoxAlreadyLocked` if the principal already has locked tokens.

4. Before the fix, the special handlers did not explicitly handle that error.

5. The error could therefore reach the generic panic branch.

6. The patch adds explicit `PoxAlreadyLocked` match arms in both PoX special handlers.

7. Those arms return `RuntimeErrorType::PoxAlreadyLocked` as a normal Clarity runtime failure.

8. The added test exercises stacking in both PoX v1 and PoX v2.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/clarity_vm/special.rs | 229 | PoX v1 special contract-call handler converts cross-version already-locked state into a Clarity runtime error instead of panicking. |
| src/clarity_vm/special.rs | 685 | PoX v2 stack-lock handler applies the same explicit PoxAlreadyLocked error mapping. |
| clarity/src/vm/errors.rs | 100 | Adds RuntimeErrorType::PoxAlreadyLocked so the VM can represent the conflict as a runtime error. |
| src/chainstate/stacks/boot/pox_2_tests.rs | 4655 | Adds regression coverage for attempting to stack in both PoX v1 and PoX v2. |

## Code Snippets

## Snippet 1

Context: `src/clarity_vm/special.rs:229` (changes a sensitive control or state-update path)

Before
```rust
return Err(Error::Runtime(RuntimeErrorType::DefunctPoxContract, None))
                    }
                    Err(e) => {
                        panic!(
```
After
```rust
return Err(Error::Runtime(RuntimeErrorType::DefunctPoxContract, None))
                    }
                    Err(ChainstateError::PoxAlreadyLocked) => {
                        // the caller tried to lock tokens into both pox-1 and pox-2
                        return Err(Error::Runtime(RuntimeErrorType::PoxAlreadyLocked, None));
                    }
                    Err(e) => {
                        panic!(
```

## Snippet 2

Context: `src/clarity_vm/special.rs:685` (changes a sensitive control or state-update path)

Before
```rust
return Err(Error::Runtime(RuntimeErrorType::DefunctPoxContract, None));
                }
                Err(e) => {
                    panic!(
```
After
```rust
return Err(Error::Runtime(RuntimeErrorType::DefunctPoxContract, None));
                }
                Err(ChainstateError::PoxAlreadyLocked) => {
                    // the caller tried to lock tokens into both pox-1 and pox-2
                    return Err(Error::Runtime(RuntimeErrorType::PoxAlreadyLocked, None));
                }
                Err(e) => {
                    panic!(
```

## Snippet 3

Context: `src/chainstate/stacks/boot/pox_2_tests.rs:4655` (changes an authorization or privilege gate)

Before
```rust
);
}
```
After
```rust
);
}

#[test]
fn stack_in_both_pox1_and_pox2() {
    // this is the number of blocks after the first sortition any V1
    // PoX locks will automatically unlock at.
    let AUTO_UNLOCK_HEIGHT = 12;
```

## Snippet 4

Context: `clarity/src/vm/errors.rs:100` (changes a sensitive control or state-update path)

Before
```rust
UnwrapFailure,
    DefunctPoxContract,
}
```
After
```rust
UnwrapFailure,
    DefunctPoxContract,
    PoxAlreadyLocked,
}
```

# Fix Pattern

Map expected lower-layer protocol rejection errors into typed VM runtime errors at the boundary instead of letting them reach panic fallback handling.

## How It Was Fixed

The patch adds `RuntimeErrorType::PoxAlreadyLocked`, updates both PoX special handlers in `src/clarity_vm/special.rs` to translate `ChainstateError::PoxAlreadyLocked` into that runtime error, and adds regression coverage in `pox_2_tests.rs`.

# Why It Matters

1. Prevents an expected PoX lock-conflict rejection from becoming panic handling.

2. Preserves the cross-version PoX lock-exclusivity rule.

3. Improves liveness behavior in a consensus-adjacent VM execution path.

4. Evidence does not establish theft, unauthorized unlocking, p2p decoding exposure, or unauthenticated remote exploitability.

# Evidence Notes

Supported by changed match arms in `src/clarity_vm/special.rs`, the new `RuntimeErrorType::PoxAlreadyLocked` enum variant in `clarity/src/vm/errors.rs`, and the added `stack_in_both_pox1_and_pox2` regression test. Traced context supports that `pox_lock_v2` can return `PoxAlreadyLocked` when tokens are already locked and that Clarity runtime errors are acceptable transaction failures. The evidence supports a panic/liveness fix, but broader exploitability claims are not established. Protocol security invariant: A principal must not lock STX simultaneously through PoX v1 and PoX v2, and attempts to do so should be rejected as ordinary Clarity runtime failures rather than reaching panic handling. Verification notes: Does not prove remote unauthenticated exploitability by itself. Does not show token theft, unauthorized unlocking, or bypass of the PoX lock-exclusivity rule. Does not establish consensus divergence; the visible risk is panic/liveness failure on an expected lock-conflict case. Does not involve p2p networking or malformed transaction decoding based on the provided evidence. No claim of p2p networking or malformed transaction decoding is supported. No claim of token theft or lock bypass is supported. No confirmed consensus divergence is shown by the supplied evidence. Security classification is likely because the changed code prevents panic handling in a protocol execution path, but exploitability details are incomplete. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unhandled-protocol-error-panic`
Final impact type: `liveness`
Final confidence: `medium`
Final tags: `clarity-vm, pox, error-handling, panic-prevention, liveness, blockchain`

The patch clearly converts an expected PoX cross-version lock conflict from a generic panic path into a typed Clarity runtime error in two special contract-call handlers, with regression coverage. That is security-relevant hardening in a consensus-adjacent protocol execution path because it removes an exposed panic condition, but the supplied evidence does not prove a concrete exploitable security bug, consensus divergence, theft, or p2p-networking issue. The original security-fix classification and p2p/database tags are too strong or misleading.

## Security Evidence

1. Adds explicit handling for ChainstateError::PoxAlreadyLocked in handle_pox_v1_api_contract_call.
2. Adds explicit handling for ChainstateError::PoxAlreadyLocked in handle_stack_lockup.
3. Previously, the provided snippets show this error would fall through to the generic panic branch.
4. Adds RuntimeErrorType::PoxAlreadyLocked so the VM can represent the condition as a runtime error.
5. Regression test stack_in_both_pox1_and_pox2 covers attempting to stack in both PoX versions.

## Missing Evidence

1. No evidence that the panic was remotely triggerable in a way that affected network availability.
2. No evidence of consensus divergence or validator disagreement.
3. No evidence of unauthorized token movement, unlocking, or bypass of PoX lock exclusivity.
4. No evidence supporting the p2p-networking subsystem classification.

## Claim Boundaries

1. Validate as security hardening, not a confirmed security fix.
2. Limit impact to liveness/panic prevention in PoX Clarity VM handling.
3. Do not claim p2p decoding, database corruption, theft, privilege escalation, or lock bypass.
4. Do not claim exploitability beyond an expected lock-conflict condition reaching panic handling.
