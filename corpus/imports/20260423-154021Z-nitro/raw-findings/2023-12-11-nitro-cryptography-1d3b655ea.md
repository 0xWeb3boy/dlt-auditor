---
case_id: case_20231211_1d3b655ea
project: nitro
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2023-12-11
source_refs:
  - git:1d3b655ea287526d3f7fc8d4be7e3c9380370dcf
  - "arbitrator/wasm-libraries/user-host/src/program.rs:61"
  - "arbitrator/prover/src/machine.rs:2506"
  - "arbitrator/wasm-libraries/user-host/src/host.rs:2"
  - "arbitrator/prover/src/error_guard.rs:103"
bug_class: incomplete-state-commitment
impact_type:
  - integrity
confidence: medium
tags:
  - blockchain-core
  - prover
  - hashing
  - state-commitment
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The strongest supported finding is a prover state-hash correctness fix: `Machine::hash` now commits the guard-enabled flag even when the guard stack is empty, and `ErrorGuardProof::hash_guards` no longer mixes that flag into the stack-hash helper. The provided evidence supports an omission in state commitment structure, but it does not by itself establish exploitability or a confirmed vulnerability.

## Observed Patch Facts

1. In `arbitrator/wasm-libraries/user-host/src/program.rs`, the patch replaces `/// Provides a reference to the current program after paying some ink.` with `/// Provides a reference to the current program.`.

2. In `arbitrator/prover/src/machine.rs`, the patch replaces `if !guards.is_empty() {` with `if !guards.is_empty() || self.guards.enabled {`.

3. In `arbitrator/wasm-libraries/user-host/src/host.rs`, the patch replaces `evm::{self, api::EvmApi, js::JsEvmApi, user::UserOutcomeKind},` with `evm::{self, api::EvmApi, user::UserOutcomeKind, EvmData},`.

4. In `arbitrator/prover/src/error_guard.rs`, the patch replaces `pub fn hash_guards(guards: &[Self], enabled: bool) -> Bytes32 {` with `pub fn hash_guards(guards: &[Self]) -> Bytes32 {`.

## Project Context

The changed code sits primarily in `arbitrator/wasm-libraries/user-host/src`, `arbitrator/wasm-libraries/user-host`, `arbitrator/prover/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `arbitrator/wasm-libraries/user-host/src/link.rs`, `arbitrator/prover/src/host.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `arbitrator/wasm-libraries/user-host/src/link.rs`, `arbitrator/prover/src/main.rs`. The strongest project-level identifiers around this patch are `guards`, `program`, `ErrorGuardProof::hash_guards`, and `api::EvmApi`. Nearby tests or test-like files include `arbitrator/prover/fuzz/fuzz_targets/osp.rs`.

## Before/After Behavior

Before the patch, `Machine::hash` only added guard-related data when `guards` was non-empty, and the enabled/disabled bit was passed indirectly through `ErrorGuardProof::hash_guards(&guards, self.guards.enabled)`. After the patch, hashing runs when guards exist or guard mode is enabled, the enabled bit is hashed explicitly, and `hash_guards` only hashes guard-stack contents with a fixed prefix.

# Root Cause

The enabled/disabled guard mode was encoded inside a helper that was only called for non-empty guard stacks, so the top-level machine hash omitted that bit in the empty-stack case.

## Walkthrough

1. In `arbitrator/prover/src/machine.rs`, the old code only entered the guard-hash path under `if !guards.is_empty()`.

2. That old path called `ErrorGuardProof::hash_guards(&guards, self.guards.enabled)`, so the mode bit was only represented when the helper was invoked.

3. In `arbitrator/prover/src/error_guard.rs`, the old helper chose different prefixes based on `enabled`, mixing mode information into the stack-hash helper.

4. The new `Machine::hash` condition is `if !guards.is_empty() || self.guards.enabled`, so the hash includes guard-related state for the empty-stack-but-enabled case.

5. The new code separately hashes a guard section marker, the enabled bit, and the guard stack hash.

6. `ErrorGuardProof::hash_guards` now hashes only guard-stack contents with a fixed prefix.

7. The `user-host` `Program` and `host` changes appear in the same commit, but the provided excerpts do not show them as the root cause of this hash-format issue.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| arbitrator/prover/src/machine.rs | 2492 | Machine state hash now commits guard mode even when the guard stack is empty. |
| arbitrator/prover/src/error_guard.rs | 94 | Error-guard stack hashing is normalized so the enabled bit is committed separately by the machine hash. |
| arbitrator/wasm-libraries/user-host/src/program.rs | 59 | Program context accessors are split (`start` vs `current`) as supporting user-host plumbing. |
| arbitrator/wasm-libraries/user-host/src/host.rs | 1 | User-host integration adopts the new program/host abstraction; appears ancillary to the commitment fix. |

## Code Snippets

## Snippet 1

Context: `arbitrator/wasm-libraries/user-host/src/program.rs:61` (changes persisted or aggregate state handling)

Before
```rust
}

    /// Provides a reference to the current program after paying some ink.
    pub fn start(cost: u64) -> &'static mut Self {
        let program = Self::start_free();
        program.buy_ink(pricing::HOSTIO_INK + cost).unwrap();
        program
    }
```
After
```rust
}

    /// Provides a reference to the current program.
    pub fn current() -> &'static mut Self {
        unsafe { PROGRAMS.last_mut().expect("no program") }
    }
}
```

## Snippet 2

Context: `arbitrator/prover/src/machine.rs:2506` (changes a sensitive control or state-update path)

Before
```rust
h.update(self.get_modules_root());

                if !guards.is_empty() {
                    h.update(ErrorGuardProof::hash_guards(&guards, self.guards.enabled));
                }
            }
```
After
```rust
h.update(self.get_modules_root());

                if !guards.is_empty() || self.guards.enabled {
                    h.update(b"With guards:");
                    h.update(&[self.guards.enabled as u8]);
                    h.update(ErrorGuardProof::hash_guards(&guards));
                }
            }
```

## Snippet 3

Context: `arbitrator/wasm-libraries/user-host/src/host.rs:2` (changes signature or replay validation logic)

Before
```rust
// For license information, see https://github.com/nitro/blob/master/LICENSE

use crate::{evm_api::ApiCaller, program::Program};
use arbutil::{
    crypto,
    evm::{self, api::EvmApi, js::JsEvmApi, user::UserOutcomeKind},
    pricing::{EVM_API_INK, HOSTIO_INK, PTR_INK},
    wavm, Bytes20, Bytes32,
```
After
```rust
// For license information, see https://github.com/nitro/blob/master/LICENSE

use crate::program::Program;
use arbutil::{
    crypto,
    evm::{self, api::EvmApi, user::UserOutcomeKind, EvmData},
    pricing::{EVM_API_INK, HOSTIO_INK, PTR_INK},
    Bytes20, Bytes32,
```

## Snippet 4

Context: `arbitrator/prover/src/error_guard.rs:103` (changes signature or replay validation logic)

Before
```rust
}

    pub fn hash_guards(guards: &[Self], enabled: bool) -> Bytes32 {
        let prefix = match enabled {
            true => Self::STACK_PREFIX_ON,
            false => Self::STACK_PREFIX_OFF,
        };
        hash_stack(guards.iter().map(|g| g.hash()), prefix)
```
After
```rust
}

    pub fn hash_guards(guards: &[Self]) -> Bytes32 {
        hash_stack(guards.iter().map(|g| g.hash()), Self::STACK_PREFIX)
    }
}
```

# Fix Pattern

Move mode or feature flags into the top-level state commitment and keep collection-hash helpers responsible only for collection contents.

## How It Was Fixed

The patch made `Machine::hash` explicitly encode guard enablement and invoke the guard section whenever guards are present or guard mode is on. It also simplified `ErrorGuardProof::hash_guards` so it hashes only the guard stack, removing the conditional encoding of the boolean from that helper.

# Why It Matters

1. It removes an identifiable omission in the machine hash format.

2. It reduces the chance that two machine configurations share the same commitment because a mode bit was skipped.

3. The affected code is in prover state hashing, which is plausibly security-relevant, but the diff alone does not prove a concrete exploit path.

# Evidence Notes

Direct support comes from the paired changes in `arbitrator/prover/src/machine.rs` and `arbitrator/prover/src/error_guard.rs`. Those hunks clearly show that guard enablement is now committed separately and in more cases than before. The `arbitrator/wasm-libraries/user-host/src/program.rs` and `arbitrator/wasm-libraries/user-host/src/host.rs` edits look like concurrent plumbing/refactor work from the provided excerpts, not independent proof of a vulnerability. The evidence does not show verifier behavior, consensus impact, reachable attacker control, or whether the omitted bit changes externally observable semantics in the empty-stack case. Protocol security invariant: The machine-state hash should explicitly commit state bits that the implementation treats as part of machine state, including guard enablement, rather than dropping them when a related collection is empty. Verification notes: The patch does not by itself prove an externally reachable exploit. The diff does not show verifier-side acceptance logic or a full consensus/fraud-proof failure path. The user-host trait changes may be refactor/supporting work rather than independently security-relevant. No memory-safety, privilege-escalation, or key-compromise claim is supported by this evidence. Deployment scope, affected releases, and real-world exploitability are not established here. No verifier-side or acceptance-path code is provided. No test diff is included in the evidence excerpts, so behavioral coverage cannot be confirmed here. The security relevance is plausible from the subsystem, but exploitability is not established by the supplied material. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `incomplete-state-commitment`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `blockchain-core, prover, hashing, state-commitment`

The patch directly changes a security-sensitive state-commitment path in the prover by ensuring the machine hash commits the guard-enabled flag even when the guard stack is empty. That is stronger than ordinary correctness work because it removes an omitted state bit from a hash used to represent machine state. However, the supplied evidence does not prove a concrete exploit, verifier bypass, or consensus break, so this is best retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. `Machine::hash` now includes guard data when `self.guards.enabled` is true even if the guard stack is empty.
2. The enabled/disabled bit is now hashed explicitly at the top-level machine hash.
3. `ErrorGuardProof::hash_guards` was simplified to hash only guard-stack contents, separating collection contents from mode state.
4. The changed code is in prover machine-state hashing, a security-sensitive integrity boundary in blockchain execution/proof code.

## Missing Evidence

1. No verifier-side or acceptance-path diff is shown.
2. No proof that `guards.enabled` changes externally observable behavior in the empty-stack case.
3. No test excerpt demonstrates a previously colliding or invalidly accepted state hash.
4. No evidence of real exploitability, affected releases, or consensus impact.

## Claim Boundaries

1. Supported claim: the commit hardens machine-state hashing by committing a previously omitted mode bit.
2. Not supported: a demonstrated exploitable vulnerability or confirmed consensus bypass.
3. Ancillary `user-host` refactor/plumbing changes are not independent security evidence from the supplied patch.
4. The safest corpus entry is a security-hardening case about incomplete state commitment, not a confirmed exploit fix.
