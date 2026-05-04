---
case_id: case_20201001_1ba4efc836
project: stacks-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2020-10-01
source_refs:
  - git:1ba4efc83662d80ca2597de4615cc9d231159efd
  - "src/vm/functions/special.rs:61"
  - "src/chainstate/stacks/boot/contract_tests.rs:1"
  - "src/chainstate/stacks/boot/pox.clar:379"
  - "src/chainstate/stacks/boot/pox.clar:572"
bug_class: delegated-stacking-validation
impact_type:
  - economic-integrity
  - consensus-validation
confidence: medium
tags:
  - pox
  - delegated-stacking
  - principal-validation
  - balance-check
  - consensus-adjacent
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adjusts PoX delegated stacking behavior: the VM special handler no longer requires the returned stacker to equal the transaction sender, and the delegated stacking path adds a balance check against `stacker`. This is plausibly security relevant, but the evidence more directly supports a delegation semantics and validation correctness fix than a confirmed vulnerability fix.

## Observed Patch Facts

1. In `src/vm/functions/special.rs`, the patch replaces `// sender is required` with `match parse_pox_stacking_result(value) {`.

2. In `src/chainstate/stacks/boot/contract_tests.rs`, the patch adds `CheckErrors, Error, IncomparableError, InterpreterError, InterpreterResult as Result,`.

3. In `src/chainstate/stacks/boot/pox.clar`, the patch replaces `;; tx-sender principal must not have rejected in this upcoming reward cycle` with `;; sender principal must not have rejected in this upcoming reward cycle`.

4. In `src/chainstate/stacks/boot/pox.clar`, the patch replaces `;; register the PoX address with the amount stacked` with `;; the Stacker must have sufficient unlocked funds`.

## Project Context

The changed code sits primarily in `src/vm/functions`, `src/vm`, `src/chainstate/stacks/boot`, which anchors the finding in the `storage` area of the project. Historical context from `src/chainstate/stacks/boot/mod.rs`, `src/vm/functions/assets.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/chainstate/stacks/db/blocks.rs`, `src/chainstate/stacks/boot/mod.rs`. The strongest project-level identifiers around this patch are `sender`, `reward`, `amount`, and `cycle`. Nearby tests or test-like files include `src/vm/tests/contracts.rs`, `src/vm/tests/assets.rs`.

## Before/After Behavior

Before the patch, `src/vm/functions/special.rs` required `sender_opt` and asserted that the parsed `stacker` matched the sender. After the patch, the handler accepts `_sender_opt`, parses the PoX stacking result, and applies `pox_lock` using the parsed `stacker`, `locked_amount`, and `unlock_height`. In `pox.clar`, the shown shared path no longer contains the `tx-sender` balance check, while the delegated stacking path adds an explicit `(stx-get-balance stacker)` check before proceeding. The delegated path also changes registration flow toward `add-pox-partial-stacked`.

# Root Cause

The prior code appears to have direct-stacking assumptions in paths that were being extended for delegated stacking. Specifically, the VM handler assumed sender and stacker were identical, and the shown Clarity checks previously used `tx-sender` in a place where delegated stacking may require reasoning about a separate `stacker` principal.

## Walkthrough

1. A PoX contract call to `stack-stx` or `delegator-stack-stx` returns a value parsed by the VM special-case handler.

2. The earlier handler required a sender and asserted that the returned stacker equaled that sender.

3. The after state removes that identity assertion and lets the native lock use the stacker returned by the contract result.

4. The shown PoX contract changes remove a sender-balance check from the shared path.

5. The delegated stacking path now checks the unlocked balance of `stacker` before continuing.

6. The added test imports indicate new or expanded regression coverage, but the imports alone do not prove a vulnerability or exploit scenario.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/vm/functions/special.rs | 49 | VM special-case PoX contract-call handler that consumes `stack-stx` and `delegator-stack-stx` return values and applies the native PoX lock |
| src/chainstate/stacks/boot/pox.clar | 373 | shared PoX stacking eligibility checks where sender-based balance validation was removed from the generic path |
| src/chainstate/stacks/boot/pox.clar | 566 | delegated stacking path where the stacker principal's unlocked balance is now explicitly checked before stacking proceeds |
| src/chainstate/stacks/boot/contract_tests.rs | 1 | regression/unit tests for PoX delegation behavior and VM/contract error handling |

## Code Snippets

## Snippet 1

Context: `src/vm/functions/special.rs:61` (changes the branch that decides whether execution stops or continues)

Before
```rust
);

        // sender is required
        let sender = match sender_opt {
            None => {
                return Err(RuntimeErrorType::NoSenderInContext.into());
            }
            Some(sender) => (*sender).clone(),
```
After
```rust
);

        match parse_pox_stacking_result(value) {
            Ok((stacker, locked_amount, unlock_height)) => {
                // if this fails, then there's a bug in the contract (since it already does
                // the necessary checks)
                match StacksChainState::pox_lock(
                    &mut global_context.database,
```

## Snippet 2

Context: `src/chainstate/stacks/boot/contract_tests.rs:1` (changes signature or replay validation logic)

Before
```rust
(no before snippet captured)
```
After
```rust
use std::collections::{HashMap, VecDeque};
use std::convert::TryFrom;

use vm::contracts::Contract;
use vm::errors::{
    CheckErrors, Error, IncomparableError, InterpreterError, InterpreterResult as Result,
    RuntimeErrorType,
};
```

## Snippet 3

Context: `src/chainstate/stacks/boot/pox.clar:379` (changes persisted or aggregate state handling)

Before
```text
(err ERR_STACKING_INVALID_AMOUNT))

    ;; tx-sender principal must not have rejected in this upcoming reward cycle
    (asserts! (is-none (get-pox-rejection tx-sender first-reward-cycle))
              (err ERR_STACKING_ALREADY_REJECTED))

    ;; the Stacker must have sufficient unlocked funds
    (asserts! (>= (stx-get-balance tx-sender) amount-ustx)
```
After
```text
(err ERR_STACKING_INVALID_AMOUNT))

    ;; sender principal must not have rejected in this upcoming reward cycle
    (asserts! (is-none (get-pox-rejection tx-sender first-reward-cycle))
              (err ERR_STACKING_ALREADY_REJECTED))

    ;; lock period must be in acceptable range.
    (asserts! (check-pox-lock-period num-cycles)
```

## Snippet 4

Context: `src/chainstate/stacks/boot/pox.clar:572` (changes persisted or aggregate state handling)

Before
```text
(err ERR_STACKING_ALREADY_STACKED))

      ;; ensure that stacking can be performed
      (try! (minimal-can-stack-stx pox-addr amount-ustx first-reward-cycle lock-period))

      ;; register the PoX address with the amount stacked
      (try! (add-pox-addr-to-reward-cycles pox-addr first-reward-cycle lock-period amount-ustx))
```
After
```text
(err ERR_STACKING_ALREADY_STACKED))

      ;; the Stacker must have sufficient unlocked funds
      (asserts! (>= (stx-get-balance stacker) amount-ustx)
        (err ERR_STACKING_INSUFFICIENT_FUNDS))

      ;; ensure that stacking can be performed
      (try! (minimal-can-stack-stx pox-addr amount-ustx first-reward-cycle lock-period))
```

# Fix Pattern

Align delegated-stacking validation with the principal being stacked, and remove direct-stacking-only sender equality assumptions from the native handler.

## How It Was Fixed

The VM special PoX handler was changed to stop requiring and comparing `sender_opt` against the parsed `stacker`. The PoX contract changes shown move sufficient-funds validation into the delegated stacking path and check `stx-get-balance` for `stacker`. The delegated registration path also appears to use partial stacking state via `add-pox-partial-stacked`.

# Why It Matters

1. Delegated stacking can involve a sender distinct from the stacker.

2. Balance checks should apply to the principal whose STX is being stacked.

3. The patch changes consensus-adjacent PoX validation behavior.

4. The provided evidence does not prove unauthorized locking, denial of service, malformed input handling, or remote exploitability.

# Evidence Notes

The strongest grounded evidence is in `src/vm/functions/special.rs` and `src/chainstate/stacks/boot/pox.clar`. The mapper's high-confidence security framing overstates what is shown: the snippets do not include the full authorization path, do not prove that `pox_lock` lacked independent safeguards, and do not show a concrete exploit or regression test body. The change may be security relevant, but the vulnerability thesis is not established from the provided input. Protocol security invariant: For PoX delegated stacking, validation and native lock application should consistently refer to the principal whose STX is being stacked, while authorization semantics must come from the PoX contract path. The provided evidence shows principal-handling changes but does not establish that the prior behavior was exploitable as a security vulnerability. Verification notes: The patch does not prove that an unauthorized delegator could lock another user's STX; authorization checks are only partially shown. The patch does not prove a node crash or panic condition despite the heuristic baseline suggesting one. The patch does not prove malformed transaction input or serialization was involved. The patch does not prove remote exploitability, only a correction to PoX delegation validation and lock handling. The test imports alone are not evidence of a security fix without the PoX contract and special-handler changes. No commands or external inspection were used, per instruction. Full diff and test bodies were not provided. Authorization checks for delegated stacking are only partially visible. No evidence proves exploitability or impact beyond validation/semantics correction. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `delegated-stacking-validation`
Final impact type: `economic-integrity, consensus-validation`
Final confidence: `medium`
Final tags: `pox, delegated-stacking, principal-validation, balance-check, consensus-adjacent`

The evidence does not prove a concrete exploitable vulnerability, but it does show a security-sensitive hardening/correctness change in PoX delegated stacking. The patch removes a direct sender-equals-stacker assumption and adds an explicit unlocked-balance check against the actual stacker principal before delegated stacking proceeds. That is stronger than a generic reliability or product change, but the original storage/liveness/p2p/signature/database framing is misleading.

## Security Evidence

1. PoX stacking affects locked funds and reward-cycle participation, making principal and balance validation security-sensitive.
2. The delegated stacking path adds an explicit `(stx-get-balance stacker)` sufficient-funds guard.
3. The VM special handler now applies `pox_lock` using the parsed `stacker` instead of requiring the transaction sender to be the stacker.
4. Context shows nearby permission and already-stacked checks in the delegated stacking flow.

## Missing Evidence

1. No exploit scenario is shown for unauthorized locking or theft.
2. Full authorization logic and full diff are not provided.
3. Test bodies are not provided, only imports and contextual snippets.
4. No evidence proves prior behavior caused consensus failure, node crash, or remote exploitability.

## Claim Boundaries

1. Validate only as security hardening, not a confirmed security fix.
2. Do not claim storage, snapshot, p2p, signature, or database impact from the supplied evidence.
3. Do not claim liveness impact beyond possible validation correctness concerns.
4. Do not claim unauthorized delegation was possible without seeing the full authorization path.
