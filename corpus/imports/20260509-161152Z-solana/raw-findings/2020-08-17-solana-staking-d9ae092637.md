---
case_id: case_20200817_d9ae092637
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
confidence: medium
source_quality: high
date: 2020-08-17
source_refs:
  - git:d9ae09263779cebedc49809799e6aa2ebbfca53c
  - "runtime/src/rent_collector.rs:50"
  - "runtime/src/rent_collector.rs:99"
  - "runtime/src/rent_collector.rs:165"
  - "runtime/src/bank.rs:4711"
bug_class: rent-exemption-recheck-bypass
impact_type:
  - protocol-accounting-integrity
tags:
  - blockchain-core
  - runtime-rent
  - rent-exemption
  - protocol-accounting
  - consensus-relevant
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a protocol accounting issue in Solana's runtime rent handling. Previously, an existing account that was rent-exempt during collection could have `rent_epoch` advanced to the next epoch even though no rent was collected. The new behavior keeps exempt accounts at the current epoch, allowing exemption to be checked again later in that epoch.

## Observed Patch Facts

1. In `runtime/src/rent_collector.rs`, the patch replaces `pub fn clone_with_epoch(&self, epoch: Epoch) -> Self {` with `operating_mode: Some(operating_mode),`.

2. In `runtime/src/rent_collector.rs`, the patch replaces `account.rent_epoch = self.epoch + 1;` with `account.rent_epoch = self.epoch`.

3. In `runtime/src/rent_collector.rs`, the patch adds `// newly created account should be collected for less rent; thus more remaining balance`.

4. In `runtime/src/bank.rs`, the patch replaces `assert_eq!(bank.get_account(&rent_exempt_pubkey).unwrap().rent_epoch, 6);` with `assert_eq!(bank.get_account(&rent_exempt_pubkey).unwrap().rent_epoch, 5);`.

## Project Context

The changed code sits primarily in `runtime/src`, which anchors the finding in the `staking` area of the project. Historical context from `runtime/src/accounts_db.rs`, `runtime/src/accounts.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/message_processor.rs`, `runtime/src/append_vec.rs`. The strongest project-level identifiers around this patch are `epoch`, `rent_epoch`, `account`, and `operating_mode`.

## Before/After Behavior

Before the patch, `collect_from_existing_account` assigned `account.rent_epoch = self.epoch + 1` for both accounts that paid rent and accounts that were currently rent-exempt. After the patch, exempt accounts under the gated new behavior use `self.epoch + 0`, while non-exempt rent collection still advances by one epoch. A bank test expectation changes the rent-exempt account's `rent_epoch` from `6` to `5`, matching the new behavior.

# Root Cause

The old logic used the same `rent_epoch` advancement for actual rent collection and for temporary rent exemption. Because exemption is computed from mutable account state, advancing `rent_epoch` for an exempt account could suppress later rechecking in the same epoch.

## Walkthrough

1. `collect_from_existing_account` skips rent work when `account.rent_epoch > self.epoch`.

2. The function computes `rent_due` and `exempt` from current account lamports, data length, and elapsed slots.

3. Before the patch, both rent-paying and exempt accounts advanced to `self.epoch + 1`.

4. The patch adds operating-mode-gated behavior for the corrected rent handling.

5. Under the new behavior, exempt accounts keep `rent_epoch` at the current epoch so they can be checked again later.

6. Regression evidence includes `test_rent_exempt_temporal_escape` and a bank-level expected `rent_epoch` change from `6` to `5`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/rent_collector.rs | 40 | Adds operating-mode-aware rent collector construction and cloning used to gate the new rent behavior. |
| runtime/src/rent_collector.rs | 76 | Main rent collection path for existing accounts, including skip conditions, rent_due calculation, and exemption handling. |
| runtime/src/rent_collector.rs | 99 | Fixes rent_epoch advancement so exempt accounts can be rechecked in the current epoch under new behavior. |
| runtime/src/rent_collector.rs | 165 | Regression coverage for rent-exempt temporal escape behavior. |
| runtime/src/bank.rs | 4705 | Bank-level test expectation updated so rent-exempt account rent_epoch remains at the current epoch. |

## Code Snippets

## Snippet 1

Context: `runtime/src/rent_collector.rs:50` (changes a consensus- or validator-sensitive branch)

Before
```rust
slots_per_year,
            rent: *rent,
        }
    }

    pub fn clone_with_epoch(&self, epoch: Epoch) -> Self {
        Self {
            epoch,
```
After
```rust
slots_per_year,
            rent: *rent,
            operating_mode: Some(operating_mode),
        }
    }

    pub fn clone_with_epoch(&self, epoch: Epoch, operating_mode: OperatingMode) -> Self {
        Self {
```

## Snippet 2

Context: `runtime/src/rent_collector.rs:99` (changes a consensus- or validator-sensitive branch)

Before
```rust
if exempt || rent_due != 0 {
                if account.lamports > rent_due {
                    account.rent_epoch = self.epoch + 1;
                    account.lamports -= rent_due;
                    rent_due
```
After
```rust
if exempt || rent_due != 0 {
                if account.lamports > rent_due {
                    account.rent_epoch = self.epoch
                        + if self.enable_new_behavior() && exempt {
                            // Rent isn't collected for the next epoch
                            // Make sure to check exempt status later in curent epoch again
                            0
                        } else {
```

## Snippet 3

Context: `runtime/src/rent_collector.rs:165` (changes a consensus- or validator-sensitive branch)

Before
```rust
assert_ne!(existing_account.rent_epoch, old_epoch);

        assert!(created_account.lamports > existing_account.lamports);
        assert_eq!(created_account.rent_epoch, existing_account.rent_epoch);
    }
}
```
After
```rust
assert_ne!(existing_account.rent_epoch, old_epoch);

        // newly created account should be collected for less rent; thus more remaining balance
        assert!(created_account.lamports > existing_account.lamports);
        assert_eq!(created_account.rent_epoch, existing_account.rent_epoch);
    }

    #[test]
```

## Snippet 4

Context: `runtime/src/bank.rs:4711` (changes the branch that decides whether execution stops or continues)

Before
```rust
large_lamports
        );
        assert_eq!(bank.get_account(&rent_exempt_pubkey).unwrap().rent_epoch, 6);
        assert_eq!(
            bank.slots_by_pubkey(&rent_due_pubkey, &ancestors),
```
After
```rust
large_lamports
        );
        assert_eq!(bank.get_account(&rent_exempt_pubkey).unwrap().rent_epoch, 5);
        assert_eq!(
            bank.slots_by_pubkey(&rent_due_pubkey, &ancestors),
```

# Fix Pattern

Separate eligibility-state advancement for actual rent collection from the handling of accounts that are only currently rent-exempt.

## How It Was Fixed

The unconditional `self.epoch + 1` assignment was replaced with conditional logic: exempt accounts under `enable_new_behavior()` advance by `0`, while other processed accounts advance by `1`. `OperatingMode` plumbing was added to gate the new behavior, and regression tests were added or updated.

# Why It Matters

1. Protects protocol rent accounting from stale exemption state.

2. Keeps rent eligibility tied to current account state.

3. Affects consensus-relevant runtime account behavior.

4. Evidence does not show theft, validator crash, memory corruption, or a complete transaction exploit sequence.

# Evidence Notes

The strongest evidence is in `runtime/src/rent_collector.rs`: `collect_from_existing_account` skips when `rent_epoch > self.epoch`, computes `exempt`, and now avoids advancing exempt accounts past the current epoch under new behavior. The inline comment explicitly says exempt status should be checked again later in the current epoch. The test name `test_rent_exempt_temporal_escape` supports the bypass interpretation. Claims about staking, state corruption broadly, theft, crashes, or consensus splits are unsupported and excluded. Protocol security invariant: Rent-exempt status must be evaluated against the account's current lamports and data size before rent processing can be skipped; a temporary exempt state must not advance rent eligibility so far that later same-epoch state changes avoid rechecking. Verification notes: No direct transaction-level exploit sequence is shown in the provided evidence. No validator crash, memory safety issue, or remote code execution is implied. No theft or unauthorized account ownership change is proven by the patch. No consensus split is demonstrated, though the changed logic is consensus-relevant runtime accounting. The stable/preview activation behavior is gated, so immediate network-wide activation is not proven from the snippet alone. Subsystem downgraded from staking to runtime-rent. Bug class narrowed to rent-exemption recheck bypass. Confidence downgraded from high to medium because no full exploit sequence or realized impact is shown. Kept as likely security because the patch fixes a protocol economic invariant rather than mere cleanup or refactor. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `rent-exemption-recheck-bypass`
Final impact type: `protocol-accounting-integrity`
Final tags: `blockchain-core, runtime-rent, rent-exemption, protocol-accounting, consensus-relevant`

The supplied patch evidence supports retaining this as security hardening, not a fully proven security fix. The change tightens Solana runtime rent accounting by preventing rent-exempt accounts from being advanced past the current epoch when no rent was collected, so exemption can be checked again later. That protects a protocol economic invariant, but the evidence does not prove a concrete exploit, theft, consensus split, crash, or staking-specific issue.

## Security Evidence

1. Runtime rent collection changed from unconditional rent_epoch advancement to conditional advancement for exempt accounts.
2. Inline comment states exempt status must be checked again later in the current epoch.
3. Regression test name test_rent_exempt_temporal_escape supports a bypass or escape scenario.
4. Bank-level test expectation changes rent_exempt account rent_epoch from 6 to 5, matching the new recheck behavior.
5. Behavior is operating-mode gated, indicating protocol-sensitive rollout rather than cosmetic cleanup.

## Missing Evidence

1. No transaction-level exploit sequence is shown.
2. No demonstrated theft, unauthorized state change, validator crash, or consensus split is provided.
3. No evidence supports the original staking subsystem label.
4. No evidence supports queue or RPC tags as part of the actual fixed behavior.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix because exploitability is not proven from the patch alone.
2. Scope is runtime rent accounting, not staking.
3. Impact should be limited to protocol accounting integrity, not broad state corruption.
4. Do not claim immediate network-wide activation because the new behavior is gated by operating mode.
