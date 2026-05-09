---
case_id: case_20230620_20a7cdd43d
project: solana
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2023-06-20
source_refs:
  - git:20a7cdd43d1dc0fa143efae79ccaf2ab22c38699
  - "core/src/validator.rs:666"
  - "ledger-tool/src/main.rs:3113"
  - "core/src/validator.rs:1671"
  - "ledger-tool/src/main.rs:2244"
bug_class: consensus-state-exposure
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - consensus
  - validator
  - bank-api
  - hard-forks
  - state-encapsulation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to harden Solana's Bank HardForks API by replacing direct lock-based access with copied hard-fork data and Bank-mediated mutation. The commit message says callers could previously obtain read/write access to HardForks and that this could cause inconsistent handling of valid hard forks. However, the supplied evidence does not establish that an untrusted actor could exploit this, that consensus divergence occurred, or that the changed call sites themselves were vulnerable. Treat this as security-relevant but not proven as a vulnerability fix.

## Observed Patch Facts

1. In `core/src/validator.rs`, the patch replaces `node.info.set_shred_version(compute_shred_version(` with `let hard_forks = bank_forks.read().unwrap().root_bank().hard_forks();`.

2. In `ledger-tool/src/main.rs`, the patch replaces `compute_shred_version(` with `compute_shred_version(&genesis_config.hash(), Some(&bank.hard_forks()))`.

3. In `core/src/validator.rs`, the patch replaces `let hard_forks: Vec<_> = bank_forks` with `leader_schedule_cache.set_fixed_leader_schedule(config.fixed_leader_schedule.clone());`.

4. In `ledger-tool/src/main.rs`, the patch replaces `Some(` with `Some(&bank_forks.read().unwrap().working_bank().hard_forks())`.

## Project Context

The changed code sits primarily in `core/src`, `ledger-tool/src`, which anchors the finding in the `consensus` area of the project. Historical context from `ledger-tool/src/program.rs`, `core/src/vote_simulator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `ledger-tool/src/program.rs`, `core/src/vote_simulator.rs`. The strongest project-level identifiers around this patch are `hard_forks`, `read`, `unwrap`, and `Some`.

## Before/After Behavior

Before the change, shown call sites accessed hard-fork state through patterns such as `bank.hard_forks().read().unwrap()` and `working_bank().hard_forks().read().unwrap()`, indicating exposure of a lockable internal object. After the change, call sites use `bank.hard_forks()` or `working_bank().hard_forks()` directly as copied hard-fork data, and validator startup logs a copied value from `root_bank().hard_forks()`.

# Root Cause

The apparent root cause was an API boundary issue: Bank exposed HardForks in a way that let internal callers obtain a lockable handle rather than only using Bank-mediated access. The provided evidence supports this as mutable state exposure, but not as a demonstrated externally exploitable flaw.

## Walkthrough

1. The commit message states that callers could previously obtain a read/write lock to HardForks from any Bank.

2. The shown validator and ledger-tool call sites previously used `.hard_forks().read().unwrap()` patterns.

3. The patch updates those sites to consume copied hard-fork data through `hard_forks()` directly.

4. The commit message says the new Bank function allows consistent sanity checks and that the getter returns a copy.

5. The supplied hunks show API adaptation in validator and ledger-tool paths, including shred-version computation inputs.

6. The evidence does not show the exact Bank-side sanity-check implementation, a reachable attacker-controlled call path, or an observed consensus failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bank.rs | 1 | core Bank API changed to mediate HardForks access and apply sanity checks |
| sdk/src/hard_forks.rs | 1 | HardForks representation/access semantics adjusted for copied getter use |
| core/src/validator.rs | 666 | validator startup reads root bank hard forks and uses them for node/shred-version related behavior |
| core/src/validator.rs | 1671 | validator ledger loading path no longer directly locks and copies working bank hard forks at call site |
| ledger-tool/src/main.rs | 2244 | ledger snapshot shred-version computation now consumes copied hard-fork state |
| ledger-tool/src/main.rs | 3113 | ledger load/reporting path computes shred version from copied Bank hard forks |

## Code Snippets

## Snippet 1

Context: `core/src/validator.rs:666` (changes a consensus- or validator-sensitive branch)

Before
```rust
Some(poh_timing_point_sender.clone()),
        )?;

        node.info.set_wallclock(timestamp());
        node.info.set_shred_version(compute_shred_version(
            &genesis_config.hash(),
            Some(
                &bank_forks
```
After
```rust
Some(poh_timing_point_sender.clone()),
        )?;
        let hard_forks = bank_forks.read().unwrap().root_bank().hard_forks();
        if !hard_forks.is_empty() {
            info!("Hard forks: {:?}", hard_forks);
        }

        node.info.set_wallclock(timestamp());
```

## Snippet 2

Context: `ledger-tool/src/main.rs:3113` (changes signature or replay validation logic)

Before
```rust
println!(
                            "Shred version: {}",
                            compute_shred_version(
                                &genesis_config.hash(),
                                Some(&bank.hard_forks().read().unwrap())
                            )
                        );
                    }
```
After
```rust
println!(
                            "Shred version: {}",
                            compute_shred_version(&genesis_config.hash(), Some(&bank.hard_forks()))
                        );
                    }
```

## Snippet 3

Context: `core/src/validator.rs:1671` (changes a consensus- or validator-sensitive branch)

Before
```rust
let pruned_banks_receiver =
        AccountsBackgroundService::setup_bank_drop_callback(bank_forks.clone());
    {
        let hard_forks: Vec<_> = bank_forks
            .read()
            .unwrap()
            .working_bank()
            .hard_forks()
```
After
```rust
let pruned_banks_receiver =
        AccountsBackgroundService::setup_bank_drop_callback(bank_forks.clone());

    leader_schedule_cache.set_fixed_leader_schedule(config.fixed_leader_schedule.clone());
```

## Snippet 4

Context: `ledger-tool/src/main.rs:2244` (changes the branch that decides whether execution stops or continues)

Before
```rust
compute_shred_version(
                                &genesis_config.hash(),
                                Some(
                                    &bank_forks
                                        .read()
                                        .unwrap()
                                        .working_bank()
                                        .hard_forks()
```
After
```rust
compute_shred_version(
                                &genesis_config.hash(),
                                Some(&bank_forks.read().unwrap().working_bank().hard_forks())
                            )
                        );
```

# Fix Pattern

Encapsulate mutable consensus-adjacent state behind an owning API; return copies for read access and route mutation through methods that can enforce checks.

## How It Was Fixed

The patch changed HardForks access semantics so call sites no longer take read locks on the internal object. Instead, Bank hard-fork access returns copied data, and the commit message says mutation is mediated by a Bank function that applies sanity checks.

# Why It Matters

1. Hard-fork state can influence validator and shred-version behavior.

2. Exposing mutable internal handles makes invariant enforcement harder.

3. Bank-mediated APIs reduce accidental inconsistent updates.

4. The provided evidence does not prove a concrete security exploit.

# Evidence Notes

Grounded evidence includes the commit message and changed call sites in `core/src/validator.rs` and `ledger-tool/src/main.rs`. The mapper lists `runtime/src/bank.rs` and `sdk/src/hard_forks.rs`, but their exact hunks are not supplied. Claims about consensus split, remote exploitability, attacker control, or confirmed vulnerability status are unsupported by the provided evidence. Protocol security invariant: A Bank's hard-fork state should be exposed through Bank-owned APIs so reads do not leak mutable internal handles and mutations can be checked consistently by the Bank. Verification notes: No concrete remote exploit path is proven by the provided patch evidence. No proof is shown that an untrusted external actor could reach a mutable HardForks handle. No demonstrated validator fork, consensus split, or safety failure is included in the evidence. The ledger-tool changes may be API adaptation rather than independently security-relevant behavior. The exact sanity checks added in runtime/src/bank.rs are described by the commit message but not shown in the provided hunks. No direct runtime Bank API diff is included in the supplied evidence. No test evidence is supplied despite tests being listed in changed files. No exploit path from untrusted input to HardForks mutation is shown. No demonstrated validator fork or safety failure is shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-state-exposure`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `consensus, validator, bank-api, hard-forks, state-encapsulation, security-hardening`

The evidence supports retaining this as security hardening, not a proven vulnerability fix. The commit message explicitly says callers could obtain read/write access to Bank HardForks from any Bank and could modify them, creating inconsistent handling of valid hard forks. The shown call sites move from exposing lock-based HardForks access to copied Bank-mediated access in validator and ledger tooling paths. That is security-relevant for consensus-adjacent state, but the supplied hunks do not prove exploitability, attacker reachability, or an actual consensus failure.

## Security Evidence

1. Commit subject and body explicitly describe restricting access to Bank HardForks.
2. Commit body says prior callers could obtain read/write locks and modify HardForks from any Bank.
3. Commit body says the change enables Bank-level sanity checks and changes the getter to return a copy.
4. Shown call sites replace `.hard_forks().read().unwrap()` access with `bank.hard_forks()` copied access.
5. Affected code includes validator and shred-version related paths, which are consensus-adjacent.

## Missing Evidence

1. No supplied hunk shows the exact `runtime/src/bank.rs` mutation API or sanity checks.
2. No demonstrated untrusted or remote path to mutate HardForks is shown.
3. No proof of a real consensus split, validator fork, or exploit is provided.
4. No regression test content is supplied despite tests being listed in changed files.

## Claim Boundaries

1. Classify as hardening of consensus-adjacent mutable state exposure, not as a confirmed exploit fix.
2. Do not claim remote exploitability from the supplied evidence.
3. Do not claim an observed consensus failure or chain safety violation.
4. Ledger-tool changes may be API adaptation rather than independently security-sensitive behavior.
