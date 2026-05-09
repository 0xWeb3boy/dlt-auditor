---
case_id: case_20180302_36bb1f989d
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: high
source_quality: high
date: 2018-03-02
source_refs:
  - git:36bb1f989d0c57cdbff9b31ed72cfa17d5221037
  - "src/accountant.rs:81"
  - "src/accountant.rs:46"
  - "src/accountant.rs:87"
  - "src/historian.rs:46"
bug_class: double-spend-stale-accounting
impact_type:
  - double-spend
  - unauthorized-spend
tags:
  - blockchain-core
  - double-spend
  - stale-balance
  - signature-validation
  - replay-protection
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

Confirmed security fix for a double-spend window in the accountant/historian transaction path. The commit explicitly states that a client could spend funds before the accountant processed a previous spend, and the patch moves signed-event validation into the accountant path while updating balances immediately rather than depending only on later historian processing.

## Observed Patch Facts

1. In `src/accountant.rs`, the patch replaces `if self.get_balance(&from).unwrap() < data {` with `from,`.

2. In `src/accountant.rs`, the patch replaces `self.historian.sender.send(event)` with `if !self.historian.verify_event(&event) {`.

3. In `src/accountant.rs`, the patch replaces `self.historian.sender.send(event)` with `if !self.historian.verify_event(&event) {`.

4. In `src/historian.rs`, the patch replaces `fn log_events<T: Serialize + Clone + Debug>(` with `fn verify_event_and_reserve_signature<T: Serialize>(`.

## Project Context

The changed code sits primarily in `src`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/event.rs`, `src/log.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/bin/demo.rs`, `src/log.rs`. The strongest project-level identifiers around this patch are `event`, `SendError`, `Event`, and `data`.

## Before/After Behavior

Before the change, signed deposit events were constructed and sent directly to the historian, and signed transfers performed balance checking before historian processing could complete. After the change, signed deposits and transfers first call `self.historian.verify_event(&event)` and reject invalid events. Deposits update `self.balances` immediately after validation, and the commit states that balances are now updated immediately to close the prior spend-before-processing window. The historian also gains a helper that verifies events and reserves seen signatures to reject duplicates before log acceptance.

# Root Cause

The accountant did not immediately reflect a previously accepted spend in local balance state, so a later spend could be checked before the earlier one had been processed. That stale-balance window allowed double-spend behavior in this transaction-accounting path.

## Walkthrough

1. A signed client operation enters the accountant as a deposit/claim or transfer event.

2. Previously, `deposit_signed` sent the claim event directly to the historian without local event verification or immediate balance update shown in the old path.

3. Previously, `transfer_signed` checked funds before the constructed transaction was sent onward, leaving the commit-described window where an earlier spend might not yet be reflected.

4. The patch makes the accountant verify signed events with `self.historian.verify_event(&event)` before accepting deposit or transfer handling.

5. Validated deposits now update the accountant balance state immediately.

6. The historian-side helper verifies events and records signatures in a `HashSet`, rejecting duplicate signatures before log acceptance.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/accountant.rs | 41 | Signed deposit path now verifies the claim event with the historian before mutating balances or sending the event for logging. |
| src/accountant.rs | 76 | Signed transfer path now verifies the transaction event, checks available balance against current accountant state, and performs immediate accounting before logging. |
| src/historian.rs | 46 | Event validation and signature reservation path rejects invalid events and duplicate signatures before log acceptance. |
| src/historian.rs | 29 | Historian log-entry creation remains the append path whose failure/validation behavior the accountant now anticipates before changing balances. |

## Code Snippets

## Snippet 1

Context: `src/accountant.rs:81` (changes the branch that decides whether execution stops or continues)

Before
```rust
sig: Signature,
    ) -> Result<(), SendError<Event<u64>>> {
        if self.get_balance(&from).unwrap() < data {
            // TODO: Replace the SendError result with a custom one.
            println!("Error: Insufficient funds");
            return Ok(());
        }
        let event = Event::Transaction {
```
After
```rust
sig: Signature,
    ) -> Result<(), SendError<Event<u64>>> {
        let event = Event::Transaction {
            from,
```

## Snippet 2

Context: `src/accountant.rs:46` (changes aggregate state or economic accounting)

Before
```rust
) -> Result<(), SendError<Event<u64>>> {
        let event = Event::Claim { key, data, sig };
        self.historian.sender.send(event)
    }

    pub fn deposit(
        self: &Self,
        n: u64,
```
After
```rust
) -> Result<(), SendError<Event<u64>>> {
        let event = Event::Claim { key, data, sig };
        if !self.historian.verify_event(&event) {
            // TODO: Replace the SendError result with a custom one.
            println!("Rejecting transaction: Invalid event");
            return Ok(());
        }
```

## Snippet 3

Context: `src/accountant.rs:87` (changes aggregate state or economic accounting)

Before
```rust
sig,
        };
        self.historian.sender.send(event)
    }
```
After
```rust
sig,
        };
        if !self.historian.verify_event(&event) {
            // TODO: Replace the SendError result with a custom one.
            println!("Rejecting transaction: Invalid event");
            return Ok(());
        }
```

## Snippet 4

Context: `src/historian.rs:46` (changes signature or replay validation logic)

Before
```rust
}

fn log_events<T: Serialize + Clone + Debug>(
    receiver: &Receiver<Event<T>>,
    sender: &SyncSender<Entry<T>>,
    signatures: &mut HashMap<Signature, bool>,
    num_hashes: &mut u64,
    end_hash: &mut Sha256Hash,
```
After
```rust
}

fn verify_event_and_reserve_signature<T: Serialize>(
    signatures: &mut HashSet<Signature>,
    event: &Event<T>,
) -> bool {
    if !verify_event(&event) {
        return false;
```

# Fix Pattern

Move validation and state reservation/update ahead of delayed logging or processing, so accepted spends immediately affect the balance state used by subsequent spend checks.

## How It Was Fixed

`src/accountant.rs` now verifies signed claim and transaction events before proceeding and rejects invalid events early. The deposit path updates balances after validation. The commit states that the accountant now updates balances immediately, and the historian-side change supports this by exposing validation behavior the accountant can check before relying on logging. `src/historian.rs` adds signature reservation using a `HashSet` so duplicate signatures are rejected in the logging path.

# Why It Matters

1. Prevents later spends from being checked against stale account balances.

2. Keeps signed-event validation before accountant acceptance.

3. Reduces dependence on later historian processing as the point where spend state becomes effective.

4. Evidence does not establish broader consensus impact or quantify exploitability.

# Evidence Notes

The strongest evidence is the commit message: `More defense against a double-spend attack`, with body text stating that a client could spend funds before the accountant processed a previous spend and that balances are now updated immediately. Code evidence shows `deposit_signed` and `transfer_signed` adding `self.historian.verify_event(&event)` rejection gates, deposit balance mutation after validation, and historian signature reservation with duplicate-signature rejection. The provided snippets do not prove arbitrary signature forgery, consensus-wide impact, practical loss amount, or that all concurrency issues are fixed. Protocol security invariant: A signed spend must not be accepted in a way that lets a later spend observe stale funds; accepted spends must immediately update or reserve accountant balance state, and signed events must be valid before the accountant relies on historian logging. Verification notes: The patch does not prove a consensus-wide vulnerability beyond this accountant/historian transaction path. The evidence does not prove arbitrary signature forgery; it shows earlier validation and replay-sensitive reservation. The evidence does not quantify financial loss or practical exploit preconditions. The evidence does not prove all concurrency or atomicity issues in the accountant are fixed. The evidence does not show remote network reachability by itself, only that signed client operations enter this path. Commit message explicitly describes a double-spend issue and the intended balance-update fix. Accountant changes show signed-event validation before acceptance paths. Deposit balance update is directly evidenced after validation. Historian duplicate-signature reservation is support code, not the primary root cause. No test evidence was provided. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `double-spend-stale-accounting`
Final impact type: `double-spend, unauthorized-spend`
Final tags: `blockchain-core, double-spend, stale-balance, signature-validation, replay-protection`

The supplied commit message explicitly describes defense against a double-spend attack and states that a client could spend funds before a previous spend was processed. The patch evidence supports that claim: signed claim and transaction paths now verify events before acceptance, balances are updated immediately in the accountant path, and historian logic reserves signatures to reject duplicates. The original replay/signature framing is somewhat too narrow because the strongest validated issue is stale accounting that enabled double spending.

## Security Evidence

1. Commit subject names a double-spend attack directly.
2. Commit body describes a spend-before-processing window and immediate balance updates as the fix.
3. accountant.rs adds historian event verification before signed deposit and transfer acceptance.
4. accountant.rs evidence shows balance mutation added after signed deposit validation and insufficient-funds rejection added after transaction validation.
5. historian.rs adds verify_event_and_reserve_signature with duplicate signature rejection using a HashSet.

## Missing Evidence

1. No tests or exploit reproduction are provided.
2. No evidence quantifies loss amount or practical attack preconditions.
3. No evidence proves consensus-wide impact beyond the accountant/historian transaction path.
4. No evidence proves arbitrary signature forgery.

## Claim Boundaries

1. Validated as a double-spend security fix in the accountant/historian accounting path.
2. Do not claim a broad consensus vulnerability from the supplied evidence alone.
3. Do not characterize the primary bug solely as signature forgery or replay; signature reservation is supporting evidence.
4. Do not claim all concurrency or atomicity issues are resolved.
