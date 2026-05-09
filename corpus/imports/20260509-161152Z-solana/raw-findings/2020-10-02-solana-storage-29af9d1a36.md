---
case_id: case_20201002_29af9d1a36
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2020-10-02
source_refs:
  - git:29af9d1a3656e4f7ef476a62c2a3545464bfe0a4
  - "runtime/src/bank.rs:2440"
  - "runtime/src/bank.rs:2458"
  - "runtime/src/bank.rs:2525"
  - "runtime/src/bank.rs:2493"
bug_class: integer-overflow-accounting
impact_type:
  - state-integrity
confidence: medium
tags:
  - runtime
  - rent-distribution
  - integer-overflow
  - accounting
  - validator
  - feature-gate
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely security-relevant accounting fix in Solana Bank rent distribution. The patch changes validator rent-share computation from `u64` intermediate multiplication to feature-gated `u128` arithmetic, then asserts that no leftover lamports remain under the corrected path. The provided evidence does not establish remote exploitability, attacker control of the required values, or a demonstrated consensus split, so the finding should remain bounded to integer-overflow accounting in runtime rent distribution.

## Observed Patch Facts

1. In `runtime/src/bank.rs`, the patch replaces `// Sort first by stake and then by validator identity pubkey for determinism` with `#[cfg(test)]`.

2. In `runtime/src/bank.rs`, the patch replaces `let rent_share =` with `let enforce_fix = self.no_overflow_rent_distribution_enabled();`.

3. In `runtime/src/bank.rs`, the patch removes `let leftover =`.

4. In `runtime/src/bank.rs`, the patch replaces `leftover_lamports` with `if enforce_fix {`.

## Project Context

The changed code sits primarily in `runtime/src`, which anchors the finding in the `storage` area of the project. Historical context from `runtime/src/serde_snapshot.rs`, `runtime/src/bloom.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/serde_snapshot.rs`, `runtime/src/bloom.rs`. The strongest project-level identifiers around this patch are `Ordering::Relaxed`, `leftover`, `rent_to_be_distributed`, and `leftover_lamports`.

## Before/After Behavior

Before the patch, each validator rent share was computed using `staked * rent_to_be_distributed` before conversion/division, so the intermediate product used `u64` arithmetic and could overflow for large values. The caller separately handled nonzero leftover lamports by warning and subtracting them from capitalization. After the patch, the corrected path is gated by `no_overflow_rent_distribution_enabled()`, computes the product and division using `u128`, converts the result back to `u64`, and asserts that fixed-mode distribution leaves zero leftover lamports. A production assertion also requires nonempty validator stakes, with a test-only fallback for bad staking state.

# Root Cause

The root cause was proportional rent-share accounting that multiplied two `u64` values before widening. If `staked * rent_to_be_distributed` overflowed, the derived validator share could be incorrect before later leftover handling.

## Walkthrough

1. Bank rent distribution calculates burned rent and `rent_to_be_distributed`, subtracts the burned portion from capitalization, and sends the distributable amount to validator distribution.

2. `distribute_rent_to_validators` collects nonzero validator stakes from vote accounts and sorts them deterministically.

3. The pre-fix share calculation used `staked * rent_to_be_distributed` as a `u64` intermediate before floating-point division by `total_staked`.

4. The patch introduces `no_overflow_rent_distribution_enabled()` and keeps the old calculation only when the feature is disabled.

5. When the feature is enabled, the patch casts operands to `u128` before multiplication and division, then converts the result back to `u64`.

6. The patch moves leftover handling into `distribute_rent_to_validators`; fixed mode asserts `leftover_lamports == 0`, while the old path retains warning and capitalization adjustment.

7. The empty-validator handling appears supportive and test-related except for the production assertion; it is not the main root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bank.rs | 2418 | Collects validator stakes from vote accounts and enforces that production rent distribution has at least one validator recipient. |
| runtime/src/bank.rs | 2458 | Computes each validator's proportional rent share; patched to use u128 intermediate multiplication when the feature is enabled. |
| runtime/src/bank.rs | 2493 | Checks and handles leftover lamports after distribution, asserting zero leftover under the fixed arithmetic path. |
| runtime/src/bank.rs | 2508 | Top-level rent distribution flow subtracts burned rent from capitalization and invokes validator distribution. |

## Code Snippets

## Snippet 1

Context: `runtime/src/bank.rs:2440` (changes a consensus- or validator-sensitive branch)

Before
```rust
.collect::<Vec<(Pubkey, u64)>>();

        // Sort first by stake and then by validator identity pubkey for determinism
        validator_stakes.sort_by(|(pubkey1, staked1), (pubkey2, staked2)| {
```
After
```rust
.collect::<Vec<(Pubkey, u64)>>();

        #[cfg(test)]
        if validator_stakes.is_empty() {
            // some tests bank.freezes() with bad staking state
            self.capitalization
                .fetch_sub(rent_to_be_distributed, Ordering::Relaxed);
            return;
```

## Snippet 2

Context: `runtime/src/bank.rs:2458` (changes the branch that decides whether execution stops or continues)

Before
```rust
});

        let validator_rent_shares = validator_stakes
            .into_iter()
            .map(|(pubkey, staked)| {
                let rent_share =
                    (((staked * rent_to_be_distributed) as f64) / (total_staked as f64)) as u64;
                rent_distributed_in_initial_round += rent_share;
```
After
```rust
});

        let enforce_fix = self.no_overflow_rent_distribution_enabled();

        let mut rent_distributed_in_initial_round = 0;
        let validator_rent_shares = validator_stakes
            .into_iter()
            .map(|(pubkey, staked)| {
```

## Snippet 3

Context: `runtime/src/bank.rs:2525` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

        let leftover =
            self.distribute_rent_to_validators(&self.vote_accounts(), rent_to_be_distributed);
        if leftover != 0 {
            warn!("There was leftover from rent distribution: {}", leftover);
            self.capitalization.fetch_sub(leftover, Ordering::Relaxed);
        }
```
After
```rust
}

        self.distribute_rent_to_validators(&self.vote_accounts(), rent_to_be_distributed);
    }
```

## Snippet 4

Context: `runtime/src/bank.rs:2493` (changes the branch that decides whether execution stops or continues)

Before
```rust
self.store_account(&pubkey, &account);
            });
        leftover_lamports
    }
```
After
```rust
self.store_account(&pubkey, &account);
            });

        if enforce_fix {
            assert_eq!(leftover_lamports, 0);
        } else if leftover_lamports != 0 {
            warn!(
                "There was leftover from rent distribution: {}",
```

# Fix Pattern

Use wider integer intermediates for proportional accounting arithmetic, gate the change for runtime rollout, and assert the corrected accounting invariant after distribution.

## How It Was Fixed

The fix adds a feature-gated branch around rent-share calculation. The fixed branch computes `((staked as u128) * (rent_to_be_distributed as u128)) / (total_staked as u128)` and converts the result with `try_into().unwrap()`. It also changes leftover handling so fixed mode asserts zero leftover lamports inside the distribution function.

# Why It Matters

1. The changed code is in Bank rent distribution, a runtime accounting path.

2. The pre-fix arithmetic could wrap before division.

3. Incorrect share calculation could misallocate validator rent distribution.

4. The patch enforces a zero-leftover condition only under the corrected arithmetic path.

5. Exploitability and attacker control are not proven by the provided evidence.

# Evidence Notes

Grounded evidence is limited to `runtime/src/bank.rs`: validator stake collection and nonempty assertion around line 2418, feature-gated `u128` share arithmetic around line 2458, leftover assertion/handling around line 2493, and the top-level rent distribution flow around line 2508. References to snapshot, bloom, append_vec, and accounts_index do not support expanding the affected subsystem beyond runtime rent distribution. Protocol security invariant: Bank rent distribution should compute validator rent shares deterministically and preserve accounting totals without overflowing intermediate arithmetic. The relevant invariant is that proportional share calculation must not wrap before division, and fixed-mode distribution should leave no unaccounted leftover lamports. Verification notes: The patch does not prove remote exploitability. The patch does not show who can cause sufficiently large `staked` and `rent_to_be_distributed` values. The patch does not prove consensus divergence, only that consensus-critical accounting could be computed incorrectly before the fix. The provided evidence does not require classifying unrelated snapshot or bloom contexts as affected paths. Supported: integer overflow risk from `u64` intermediate multiplication before division. Supported: feature-gated fix using `u128` arithmetic. Supported: fixed path asserts zero leftover lamports. Not established: remote exploitability. Not established: attacker control of large stake and rent values. Not established: concrete consensus divergence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `integer-overflow-accounting`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `runtime, rent-distribution, integer-overflow, accounting, validator, feature-gate`

The patch clearly removes a u64 intermediate overflow risk from Solana runtime rent distribution by feature-gating wider u128 proportional-share arithmetic and asserting the corrected leftover invariant. That is security-relevant hardening for consensus-sensitive accounting, but the supplied evidence does not prove attacker control, concrete exploitation, or an observed consensus failure, so security-fix is too strong.

## Security Evidence

1. Rent distribution used staked * rent_to_be_distributed with u64 operands before widening/division.
2. The fixed path casts operands to u128 before multiplication and division.
3. The behavior is feature-gated through no_overflow_rent_distribution_enabled(), indicating runtime rollout of a corrected invariant.
4. Fixed mode asserts leftover_lamports == 0 after distribution.
5. The code runs in Bank validator rent distribution, a consensus-sensitive accounting path.

## Missing Evidence

1. No proof that an attacker can force the required stake and rent values.
2. No demonstrated exploit, loss, theft, or consensus split is shown.
3. No test output or advisory proves this was treated as a vulnerability.
4. Related snapshot, bloom, append_vec, and accounts_index context does not support the storage/queue framing.

## Claim Boundaries

1. Classify as security-hardening, not confirmed security-fix.
2. Limit the bug class to integer overflow in runtime rent-distribution accounting.
3. Do not claim remote exploitability or attacker-controlled inputs from this evidence.
4. Do not expand the affected subsystem beyond Bank rent distribution and validator accounting.
