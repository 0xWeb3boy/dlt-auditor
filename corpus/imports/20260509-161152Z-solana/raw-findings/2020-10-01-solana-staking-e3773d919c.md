---
case_id: case_20201001_e3773d919c
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2020-10-01
source_refs:
  - git:e3773d919cf80f58918136cc604b05464c1bec8a
  - "runtime/src/bank.rs:2430"
  - "runtime/src/bank.rs:2448"
  - "runtime/src/bank.rs:2513"
  - "runtime/src/bank.rs:2483"
bug_class: integer-overflow
impact_type:
  - economic-integrity
  - consensus-integrity
confidence: medium
tags:
  - runtime
  - rent-distribution
  - integer-overflow
  - economic-accounting
  - consensus
  - validator-accounting
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports an overflow-prone rent distribution calculation in Solana runtime accounting, but it does not establish an exploitable security vulnerability. The patch replaces `u64` intermediate multiplication in validator rent-share calculation with feature-gated `u128` arithmetic and tightens leftover lamport handling. This is plausibly security-relevant consensus/economic hardening, but the vulnerability thesis is not proven from the supplied evidence.

## Observed Patch Facts

1. In `runtime/src/bank.rs`, the patch replaces `// Sort first by stake and then by validator identity pubkey for determinism` with `#[cfg(test)]`.

2. In `runtime/src/bank.rs`, the patch replaces `let rent_share =` with `let enforce_fix = self.no_overflow_rent_distribution_enabled();`.

3. In `runtime/src/bank.rs`, the patch removes `let leftover =`.

4. In `runtime/src/bank.rs`, the patch replaces `leftover_lamports` with `if enforce_fix {`.

## Project Context

The changed code sits primarily in `runtime/src`, which anchors the finding in the `staking` area of the project. Historical context from `runtime/src/stakes.rs`, `runtime/src/vote_sender_types.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/stakes.rs`. The strongest project-level identifiers around this patch are `leftover`, `rent_to_be_distributed`, `leftover_lamports`, and `validator_stakes`.

## Before/After Behavior

Before the patch, validator rent shares were computed with `staked * rent_to_be_distributed` in `u64` arithmetic before conversion to `f64` and division by `total_staked`, which could overflow the intermediate product. Leftover lamports were returned to the caller, logged, and subtracted from capitalization. After the patch, the feature-enabled path computes the product and division in `u128`, converts the result back to `u64`, asserts zero leftover lamports inside the distribution function, and removes caller-side leftover reconciliation. The patch also adds explicit handling for an empty validator stake set: tests adjust capitalization and return, while production asserts non-empty validator stakes.

# Root Cause

The root cause was an overflow-prone intermediate multiplication in rent-share accounting: both `staked` and `rent_to_be_distributed` were `u64`, and their product was calculated before division. The provided evidence does not show that an attacker can control these values, trigger a crash, steal funds, or cause consensus divergence.

## Walkthrough

1. `distribute_rent()` calculates the distributable rent amount and calls `distribute_rent_to_validators()`.

2. `distribute_rent_to_validators()` collects nonzero validator stakes from vote accounts and sums `total_staked`.

3. The patch adds handling for an empty validator stake set, with different test and production behavior.

4. Validators are sorted deterministically by stake and pubkey.

5. The legacy calculation computes each rent share using `staked * rent_to_be_distributed` as `u64`.

6. The feature-enabled fixed path casts the operands to `u128`, performs multiplication and division in the wider type, and converts the result back to `u64`.

7. The fixed path asserts that `leftover_lamports` is zero after distribution.

8. The caller no longer handles leftover lamports because that logic moved into the distribution function.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bank.rs | 2430 | Handles empty validator stake set before rent distribution; production path asserts non-empty state while tests retain capitalization adjustment. |
| runtime/src/bank.rs | 2448 | Computes each validator's proportional rent share; patched path uses u128 multiplication/division to avoid u64 overflow. |
| runtime/src/bank.rs | 2483 | Validates post-distribution leftover lamports; fixed path asserts zero leftover instead of silently adjusting capitalization. |
| runtime/src/bank.rs | 2513 | Calls validator rent distribution from bank rent distribution without caller-side leftover reconciliation after the distribution function internalizes the invariant. |
| runtime/src/feature_set.rs | 0 | Introduces or wires the feature gate controlling the corrected no-overflow rent distribution behavior. |
| runtime/src/snapshot_utils.rs | 0 | Touched as part of feature/runtime baseline update, but provided evidence does not show it as the primary bug path. |

## Code Snippets

## Snippet 1

Context: `runtime/src/bank.rs:2430` (changes a consensus- or validator-sensitive branch)

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
                .fetch_sub(rent_to_be_distributed, Relaxed);
            return;
```

## Snippet 2

Context: `runtime/src/bank.rs:2448` (changes the branch that decides whether execution stops or continues)

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

Context: `runtime/src/bank.rs:2513` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

        let leftover =
            self.distribute_rent_to_validators(&self.vote_accounts(), rent_to_be_distributed);
        if leftover != 0 {
            warn!("There was leftover from rent distribution: {}", leftover);
            self.capitalization.fetch_sub(leftover, Relaxed);
        }
```
After
```rust
}

        self.distribute_rent_to_validators(&self.vote_accounts(), rent_to_be_distributed);
    }
```

## Snippet 4

Context: `runtime/src/bank.rs:2483` (changes the branch that decides whether execution stops or continues)

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

Use widened integer arithmetic for proportional accounting calculations and enforce the post-distribution accounting invariant at the point where the distribution is computed.

## How It Was Fixed

The patch introduces `self.no_overflow_rent_distribution_enabled()` and, when enabled, calculates rent shares as `((staked as u128) * (rent_to_be_distributed as u128)) / (total_staked as u128)` followed by conversion back to `u64`. It also asserts non-empty validator stakes in production, asserts zero leftover lamports in the fixed path, and removes caller-side leftover handling from `distribute_rent()`.

# Why It Matters

1. Prevents overflow in validator rent-share arithmetic.

2. Improves correctness of runtime economic accounting.

3. Tightens leftover lamport handling into an asserted invariant.

4. Security impact is not established by the provided evidence.

# Evidence Notes

The supported evidence is limited to `runtime/src/bank.rs` changes around rent distribution. `runtime/src/feature_set.rs` appears to support feature gating, and `runtime/src/snapshot_utils.rs` appears to be supporting context, but neither is shown as the root cause. Claims about malformed transaction input, direct attacker control, node crash, fund theft, or consensus divergence are unsupported by the supplied evidence. Protocol security invariant: Runtime rent distribution should compute validator rent shares deterministically and preserve lamport accounting without overflowing intermediate arithmetic. Verification notes: The patch does not prove that an external attacker can choose `staked` or `rent_to_be_distributed` values directly. The patch does not show malformed transaction decoding or signature input reaching this arithmetic path. The patch does not establish a node crash in release builds; it shows overflow-prone accounting arithmetic being replaced. The evidence supports consensus/economic accounting hardening, not a demonstrated fund theft or privilege bypass. The snapshot and feature-set changes are supporting context only from the provided evidence. Code evidence supports `integer-overflow` as the bug class. Code evidence supports `runtime-rent-distribution` as the subsystem. Exploitability is not demonstrated. Direct attacker control of `staked` or `rent_to_be_distributed` is not demonstrated. Keep out of the security corpus because the security vulnerability thesis remains unclear. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `integer-overflow`
Final impact type: `economic-integrity, consensus-integrity`
Final confidence: `medium`
Final tags: `runtime, rent-distribution, integer-overflow, economic-accounting, consensus, validator-accounting`

The patch clearly removes an overflow-prone u64 multiplication from Solana runtime rent distribution and replaces it with feature-gated u128 arithmetic while tightening lamport leftover invariants. The evidence does not prove a concrete exploitable vulnerability, attacker control, fund theft, or chain halt, so this should not be treated as a confirmed security fix. However, because the affected code is protocol runtime economic accounting for validator rent distribution, the change is security-relevant hardening and belongs in the corpus with conservative metadata.

## Security Evidence

1. Runtime rent-share calculation changed from u64 intermediate multiplication to u128 arithmetic.
2. The changed path distributes lamports to validators based on stake and rent collected.
3. Feature gate no_overflow_rent_distribution_enabled indicates a protocol behavior correction.
4. The fixed path asserts zero leftover lamports instead of tolerating accounting drift.
5. Production now asserts non-empty validator stakes for this distribution path.

## Missing Evidence

1. No evidence that an attacker can directly control staked or rent_to_be_distributed to trigger overflow.
2. No demonstrated exploit, fund theft, privilege bypass, or denial of service.
3. No evidence of actual consensus divergence before the patch.
4. No test or advisory evidence showing a security incident or reachable attack scenario.

## Claim Boundaries

1. Classify as security-hardening, not a confirmed security-fix.
2. Do not claim direct attacker exploitability from the supplied patch alone.
3. Do not retain the original liveness-failure framing; the supported issue is overflow in economic accounting.
4. Snapshot and feature-set files are supporting context only, not primary vulnerability evidence.
