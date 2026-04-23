---
case_id: case_20231121_995df9e00
project: nitro
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: core-logic
source_quality: high
date: 2023-11-21
source_refs:
  - git:995df9e00b1d9f97f5a4d57f7210b592c2306a6c
  - "arbitrator/prover/src/machine.rs:1715"
  - "arbitrator/prover/src/machine.rs:783"
  - "arbitrator/prover/src/machine.rs:2317"
  - "arbitrator/wasm-libraries/user-host/src/evm_api.rs:7"
bug_class: error-handling-policy
impact_type:
  - execution-integrity
confidence: medium
tags:
  - infrastructure
  - core-logic
  - vm
  - error-handling
  - policy-guard
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes the prover VM's error-guard behavior from implicitly recovering whenever a guard frame exists to recovering only when an explicit `enabled` policy bit is set. That is a real control-flow hardening change, but the provided evidence does not establish a concrete vulnerability, attacker trigger, or protocol impact.

## Observed Patch Facts

1. In `arbitrator/prover/src/machine.rs`, the patch replaces `if let Some(guard) = self.guards.pop() {` with `if self.guards.enabled && !self.guards.is_empty() {`.

2. In `arbitrator/prover/src/machine.rs`, the patch replaces `pub struct ErrorGuard {` with `pub struct Machine {`.

3. In `arbitrator/prover/src/machine.rs`, the patch replaces `Opcode::HaltAndSetFinished => {` with `self.guards.enabled = true;`.

4. In `arbitrator/wasm-libraries/user-host/src/evm_api.rs`, the patch adds `#[link(wasm_import_module = "hostio")]`.

## Project Context

The changed code sits primarily in `arbitrator/prover/src`, `arbitrator/prover`, `arbitrator/wasm-libraries/user-host/src`, which anchors the finding in the `core-logic` area of the project. Historical context from `arbitrator/prover/src/error_guard.rs`, `arbitrator/prover/src/wavm.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `arbitrator/prover/src/error_guard.rs`, `arbitrator/prover/src/wavm.rs`. The strongest project-level identifiers around this patch are `guards`, `enabled`, `usize`, and `Opcode::PopErrorGuard`. Nearby tests or test-like files include `arbitrator/prover/fuzz/fuzz_targets/osp.rs`.

## Before/After Behavior

Before the patch, the error path in `arbitrator/prover/src/machine.rs` recovered on `if let Some(guard) = self.guards.pop()`, so guard presence alone controlled recovery. After the patch, recovery requires `self.guards.enabled && !self.guards.is_empty()`, `PushErrorGuard` sets `enabled = true`, `PopErrorGuard` sets `enabled = false`, and a new `SetErrorPolicy` opcode can toggle the policy explicitly.

# Root Cause

Recovery authorization was inferred from residual guard-stack contents instead of a separate explicit policy flag.

## Walkthrough

1. The fault path in `machine.rs` stops treating `Some(guard)` as sufficient and now checks both `enabled` and non-empty guard state before recovery.

2. The guard stack representation includes an explicit `enabled` boolean in `error_guard.rs`, showing policy state was separated from stored guard frames.

3. `PushErrorGuard` and `PopErrorGuard` now update that policy bit in `machine.rs`.

4. A new `SetErrorPolicy` opcode sets `self.guards.enabled = status != 0`, making policy changes explicit rather than incidental.

5. Related WAVM and host-interface changes wire that opcode through the runtime surface, including the new `wavm_set_error_policy(status: u32)` import.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| arbitrator/prover/src/machine.rs | 1694 | core VM fault/recovery path that decides whether an execution error is caught by an error guard |
| arbitrator/prover/src/machine.rs | 2311 | opcode handlers that push/pop guards and now toggle guard-policy state |
| arbitrator/prover/src/error_guard.rs | 11 | error-guard stack structure extended with explicit `enabled` policy state |
| arbitrator/prover/src/wavm.rs | 284 | WAVM opcode surface defining `SetErrorPolicy` as part of machine semantics |
| arbitrator/prover/src/host.rs | 146 | host function typing for the new error-policy control path |
| arbitrator/wasm-libraries/user-host/src/evm_api.rs | 7 | guest-to-host import exposing error-policy changes to user-host code |

## Code Snippets

## Snippet 1

Context: `arbitrator/prover/src/machine.rs:1715` (changes the branch that decides whether execution stops or continues)

Before
```rust
};

                if let Some(guard) = self.guards.pop() {
                    if self.debug_info {
                        print_debug_info(self);
```
After
```rust
};

                if self.guards.enabled && !self.guards.is_empty() {
                    let guard = self.guards.pop().unwrap();
                    if self.debug_info {
                        print_debug_info(self);
```

## Snippet 2

Context: `arbitrator/prover/src/machine.rs:783` (changes signature or replay validation logic)

Before
```rust
}

#[derive(Clone, Debug)]
pub struct ErrorGuard {
    frame_stack: usize,
    value_stack: usize,
    inter_stack: usize,
    on_error: ProgramCounter,
```
After
```rust
}

#[derive(Clone, Debug)]
pub struct Machine {
```

## Snippet 3

Context: `arbitrator/prover/src/machine.rs:2317` (changes the branch that decides whether execution stops or continues)

Before
```rust
});
                    self.value_stack.push(1_u32.into());
                    reset_refs!();
                }
                Opcode::PopErrorGuard => {
                    self.guards.pop();
                }
                Opcode::HaltAndSetFinished => {
```
After
```rust
});
                    self.value_stack.push(1_u32.into());
                    self.guards.enabled = true;
                    reset_refs!();
                }
                Opcode::PopErrorGuard => {
                    self.guards.pop();
                    self.guards.enabled = false;
```

## Snippet 4

Context: `arbitrator/wasm-libraries/user-host/src/evm_api.rs:7` (changes a sensitive control or state-update path)

Before
```rust
};

#[link(wasm_import_module = "go_stub")]
extern "C" {
```
After
```rust
};

#[link(wasm_import_module = "hostio")]
extern "C" {
    fn wavm_set_error_policy(status: u32);
}

#[link(wasm_import_module = "go_stub")]
```

# Fix Pattern

Add explicit policy state for recovery behavior and enforce it at the decision point instead of inferring permission from leftover internal state.

## How It Was Fixed

The fix introduced an `enabled` flag on the error-guard stack, required that flag in the machine's recovery branch, and added opcode/host plumbing so the policy can be set deliberately.

# Why It Matters

1. It makes VM fault handling more explicit and less dependent on stale internal state.

2. It reduces the chance that leftover guard frames affect later error handling unintentionally.

3. The change is in a sensitive execution path, but the evidence does not prove a security exploit or consensus failure.

# Evidence Notes

The strongest support is the direct change in `arbitrator/prover/src/machine.rs` from popping any available guard to requiring `self.guards.enabled`, plus the added `enabled` field and `SetErrorPolicy` plumbing. The evidence supports a claim of error-handling hardening. It does not prove attacker reachability, real-world exploitability, fund risk, or an actual protocol break. Protocol security invariant: Fault recovery in the prover VM should occur only when error-guard handling is explicitly enabled for the current execution scope and a guard frame is present. Verification notes: The patch does not by itself prove a practical exploit or attacker-controlled trigger path. The patch does not show that mainnet or consensus divergence actually occurred. It is not proven that funds could be stolen; the strongest supported claim is deterministic execution/proving semantics hardening. The patch does not show cryptographic breakage; the concern is control-flow and state-policy correctness. It is not proven whether this was reachable from untrusted contracts in all deployment modes. Grounded in the shown before/after code snippets for the recovery branch and opcode handlers. Supported by traced context showing `ErrorGuardStack { guards, enabled }` in `error_guard.rs`. Supported by the addition of `SetErrorPolicy` in WAVM/host plumbing. Not enough evidence to confirm a concrete vulnerability rather than a semantics cleanup or hardening change. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `error-handling-policy`
Final impact type: `execution-integrity`
Final confidence: `medium`
Final tags: `infrastructure, core-logic, vm, error-handling, policy-guard`

The patch supports a security-hardening interpretation, not a proven vulnerability fix. In a sensitive prover/VM execution path, it changes error recovery from implicitly triggering whenever a guard frame exists to requiring an explicit enabled policy bit, and it adds opcode/host plumbing to control that policy deliberately. That clearly tightens failure-handling semantics and removes a risky stale-state condition, but the supplied evidence does not prove attacker reachability, exploitable consensus impact, or a concrete security incident.

## Security Evidence

1. The main recovery branch now requires both `self.guards.enabled` and a non-empty guard stack before recovering from an error.
2. `PushErrorGuard` sets `self.guards.enabled = true` and `PopErrorGuard` sets it to `false`, making recovery authorization explicit rather than incidental.
3. A new `SetErrorPolicy` opcode and `wavm_set_error_policy(status)` host import were added, showing deliberate policy control across the runtime boundary.
4. The change is in prover/VM control-flow and error handling, a security-sensitive area for deterministic execution semantics.

## Missing Evidence

1. No proof that stale guard state was attacker-controllable from untrusted input or contracts.
2. No demonstrated exploit, consensus divergence, fund impact, or concrete integrity break.
3. No commit message or test evidence explicitly describing a security bug or vulnerability scenario.

## Claim Boundaries

1. Supported claim: the patch hardens VM error-recovery semantics by requiring explicit policy enablement.
2. Supported claim: it reduces risk from unintended recovery caused by leftover guard state.
3. Not supported: a confirmed exploitable vulnerability, consensus break, or direct fund-loss condition.
4. Not supported: the original stronger framing of `state-corruption` as a demonstrated bug class.
