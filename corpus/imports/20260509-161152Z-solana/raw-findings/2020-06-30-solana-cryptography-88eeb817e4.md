---
case_id: case_20200630_88eeb817e4
project: solana
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2020-06-30
source_refs:
  - git:88eeb817e4f3dc873e34f11d330d93ec25dcff39
  - "core/src/validator.rs:708"
  - "validator/src/main.rs:906"
  - "core/src/validator.rs:394"
  - "core/src/validator.rs:702"
bug_class: validator-restart-precondition-hardening
impact_type:
  - consensus-safety
  - validator-startup-safety
confidence: medium
tags:
  - validator-ops
  - consensus
  - restart
  - ledger
  - supermajority
  - fail-fast
  - configuration-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds restart guard rails for Solana validator startup. `wait_for_supermajority` now returns an error signal when the configured wait slot is greater than the local bank slot, and startup exits on that signal. The validator config path also begins parsing `expected_bank_hash`. The evidence supports operational restart safety hardening, but does not establish a concrete vulnerability, attacker path, or exploitable consensus failure.

## Observed Patch Facts

1. In `core/src/validator.rs`, the patch replaces `) {` with `) -> bool {`.

2. In `validator/src/main.rs`, the patch adds `expected_bank_hash: matches`.

3. In `core/src/validator.rs`, the patch replaces `wait_for_supermajority(config, &bank, &cluster_info, rpc_override_health_check);` with `if wait_for_supermajority(config, &bank, &cluster_info, rpc_override_health_check) {`.

4. In `core/src/validator.rs`, the patch adds `// Return true on error, indicating the validator should exit.`.

## Project Context

The changed code sits primarily in `core/src`, `validator/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/src/banking_stage.rs`, `core/src/rpc.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/rpc.rs`, `core/src/window_service.rs`. The strongest project-level identifiers around this patch are `wait_for_supermajority`, `Hash::from_str`, `config`, and `bank`.

## Before/After Behavior

Before, `wait_for_supermajority` returned silently unless `config.wait_for_supermajority` exactly matched `bank.slot()`, so a validator with a local bank slot behind the configured restart slot could continue startup in the visible path. After, the helper compares the configured slot to `bank.slot()`, returns true on the behind-ledger case, and the startup path exits with status 1. Separately, `expected_bank_hash` is now parsed into `ValidatorConfig`.

# Root Cause

The visible restart helper treated all non-equal supermajority-slot cases as no-op returns, without distinguishing a harmless already-past condition from the unsafe-looking case where the local ledger was behind the configured restart slot.

## Walkthrough

1. A validator starts with `wait_for_supermajority` configured.

2. The local `bank.slot()` may be lower than the configured supermajority wait slot.

3. Before the patch, the helper returned immediately because the slots were not exactly equal.

4. Startup then continued in the visible call path.

5. After the patch, the helper detects the configured-greater-than-local case.

6. The helper logs an insufficient-ledger error and returns true.

7. The startup call site exits when that error signal is returned.

8. `expected_bank_hash` is also parsed into validator configuration, though the supplied evidence does not show its enforcement.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/validator.rs | 394 | validator startup now exits when wait_for_supermajority reports an unrecoverable ledger/supermajority mismatch |
| core/src/validator.rs | 705 | restart guard compares configured wait_for_supermajority slot against the local bank slot and returns an error condition when ledger data is insufficient |
| validator/src/main.rs | 906 | validator CLI/config path parses expected_bank_hash into ValidatorConfig for restart validation |

## Code Snippets

## Snippet 1

Context: `core/src/validator.rs:708` (changes signature or replay validation logic)

Before
```rust
cluster_info: &ClusterInfo,
    rpc_override_health_check: Arc<AtomicBool>,
) {
    if config.wait_for_supermajority != Some(bank.slot()) {
        return;
    }
```
After
```rust
cluster_info: &ClusterInfo,
    rpc_override_health_check: Arc<AtomicBool>,
) -> bool {
    if let Some(wait_for_supermajority) = config.wait_for_supermajority {
        match wait_for_supermajority.cmp(&bank.slot()) {
            std::cmp::Ordering::Less => return false,
            std::cmp::Ordering::Greater => {
                error!("Ledger does not have enough data to wait for supermajority, please enable snapshot fetch. Has {} needs {}", bank.slot(), wait_for_supermajority);
```

## Snippet 2

Context: `validator/src/main.rs:906` (changes signature or replay validation logic)

Before
```rust
.value_of("expected_genesis_hash")
            .map(|s| Hash::from_str(&s).unwrap()),
        expected_shred_version: value_t!(matches, "expected_shred_version", u16).ok(),
        new_hard_forks: hardforks_of(&matches, "hard_forks"),
```
After
```rust
.value_of("expected_genesis_hash")
            .map(|s| Hash::from_str(&s).unwrap()),
        expected_bank_hash: matches
            .value_of("expected_bank_hash")
            .map(|s| Hash::from_str(&s).unwrap()),
        expected_shred_version: value_t!(matches, "expected_shred_version", u16).ok(),
        new_hard_forks: hardforks_of(&matches, "hard_forks"),
```

## Snippet 3

Context: `core/src/validator.rs:394` (changes a sensitive control or state-update path)

Before
```rust
};

        wait_for_supermajority(config, &bank, &cluster_info, rpc_override_health_check);

        let poh_service = PohService::new(poh_recorder.clone(), &poh_config, &exit);
```
After
```rust
};

        if wait_for_supermajority(config, &bank, &cluster_info, rpc_override_health_check) {
            std::process::exit(1);
        }

        let poh_service = PohService::new(poh_recorder.clone(), &poh_config, &exit);
```

## Snippet 4

Context: `core/src/validator.rs:702` (changes a sensitive control or state-update path)

Before
```rust
}

fn wait_for_supermajority(
    config: &ValidatorConfig,
```
After
```rust
}

// Return true on error, indicating the validator should exit.
fn wait_for_supermajority(
    config: &ValidatorConfig,
```

# Fix Pattern

Convert a silent restart precondition helper into an explicit fail-fast guard, and propagate configured expected state into validator configuration.

## How It Was Fixed

`core/src/validator.rs` changed `wait_for_supermajority` to return `bool`, with true indicating startup should exit. It now compares the configured supermajority slot with the local bank slot and exits startup when the local ledger lacks enough data. `validator/src/main.rs` now parses `expected_bank_hash` from matches into `ValidatorConfig`.

# Why It Matters

1. Prevents continuing startup with insufficient local ledger data for the configured restart slot.

2. Makes a restart precondition failure explicit instead of silently skipped.

3. Adds config plumbing for an expected bank hash.

4. Does not prove a remote exploit or confirmed consensus vulnerability from the supplied snippets.

# Evidence Notes

Grounded evidence is limited to validator startup behavior in `core/src/validator.rs` and config parsing in `validator/src/main.rs`. The claim that this fixes replay validation, signature validation, or a demonstrated consensus exploit is unsupported. The ledger-tool snapshot hash printing mentioned in the commit body is not included in the supplied enforcing-code evidence. Protocol security invariant: During coordinated validator restart, a validator should not continue startup when its local bank slot is behind the configured supermajority wait slot. The supplied evidence also shows expected_bank_hash is passed into ValidatorConfig, but does not show the enforcing check. Verification notes: No remote attacker path is proven by the patch evidence. No transaction signature verification bypass is shown. No replay-attack primitive is shown despite hash and ledger terminology. The evidence supports hardening/fail-fast behavior for coordinated restart, not a confirmed consensus exploit. The ledger-tool snapshot hash printing mentioned in the commit body is not shown to enforce a security check. No tests are shown in the supplied evidence. No attacker-controlled input path is shown. No enforcement site for `expected_bank_hash` is shown. Behavioral change is well supported for the local-bank-slot-behind-configured-slot case. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `validator-restart-precondition-hardening`
Final impact type: `consensus-safety, validator-startup-safety`
Final confidence: `medium`
Final tags: `validator-ops, consensus, restart, ledger, supermajority, fail-fast, configuration-validation`

The supplied patch evidence supports a conservative security-hardening classification: validator startup now fails closed when the configured supermajority wait slot is ahead of the local bank slot, preventing operation with insufficient ledger state during a sensitive restart procedure. The evidence does not support the original replay/signature-validation framing or a concrete exploitable vulnerability.

## Security Evidence

1. Validator startup path now exits when wait_for_supermajority reports an error.
2. wait_for_supermajority distinguishes already-past, exact, and local-ledger-behind cases instead of silently returning for all mismatches.
3. The behind-ledger case logs that the ledger lacks enough data for the configured supermajority slot.
4. expected_bank_hash is parsed into ValidatorConfig, indicating additional restart-state validation plumbing.

## Missing Evidence

1. No attacker-controlled input path is shown.
2. No concrete exploit, consensus split, replay, or signature-validation bypass is demonstrated.
3. No enforcement site for expected_bank_hash is included in the supplied evidence.
4. No tests or incident context are provided.

## Claim Boundaries

1. Keep as validator restart and consensus-safety hardening, not as a confirmed vulnerability fix.
2. Do not classify this as replay protection or signature validation.
3. Do not claim expected_bank_hash is enforced beyond config parsing from the supplied patch.
4. Do not claim remote exploitability from this evidence alone.
