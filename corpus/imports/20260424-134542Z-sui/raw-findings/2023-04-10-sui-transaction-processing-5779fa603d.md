---
case_id: case_20230410_5779fa603d
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2023-04-10
source_refs:
  - git:5779fa603d9f0706ab91b947c61575dde9fb2ae0
  - "crates/sui-adapter/src/execution_engine.rs:312"
  - "crates/sui-config/src/node.rs:275"
  - "crates/sui-core/src/authority.rs:987"
  - "crates/sui-config/src/node.rs:337"
bug_class: monetary-accounting-invariant-hardening
impact_type:
  - asset-integrity
confidence: medium
tags:
  - transaction-processing
  - accounting-invariant
  - sui-conservation
  - safety-check
  - config-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds configuration plumbing for an expensive deep per-transaction SUI conservation check in Sui transaction execution. It introduces `enable_deep_per_tx_sui_conservation_check` in node configuration, exposes an accessor that also enables the check in debug builds, and passes the resulting flag from authority certificate preparation into transaction execution. The evidence supports security-relevant hardening around a monetary accounting invariant, but it does not establish a concrete pre-patch vulnerability, exploit path, accounting bypass, or production-default enforcement change.

## Observed Patch Facts

1. In `crates/sui-adapter/src/execution_engine.rs`, the patch changes a sensitive implementation path.

2. In `crates/sui-config/src/node.rs`, the patch replaces `#[serde(default)]` with `/// If enabled, we will check that the total SUI in all input objects of a tx`.

3. In `crates/sui-core/src/authority.rs`, the patch adds `// TODO: would be nice to pass the whole NodeConfig here, but it creates a`.

4. In `crates/sui-config/src/node.rs`, the patch adds `pub fn enable_deep_per_tx_sui_conservation_check(&self) -> bool {`.

## Project Context

The changed code sits primarily in `crates/sui-adapter/src`, `crates/sui-adapter`, `crates/sui-config/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/sui-config/src/genesis.rs`, `crates/sui-core/src/transaction_orchestrator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-config/src/genesis.rs`, `crates/sui-core/src/authority/authority_store.rs`. The strongest project-level identifiers around this patch are `epoch`, `need`, `rewards`, and `rebates`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/execution_driver_tests.rs`, `crates/sui-core/src/unit_tests/epoch_data_tests.rs`.

## Before/After Behavior

Before the patch, the provided authority execution call passed epoch data and protocol config into `execute_transaction_to_effects` without a visible node-config flag controlling a deep per-transaction SUI conservation check. After the patch, node configuration includes `enable_deep_per_tx_sui_conservation_check`, its accessor returns the configured value or `cfg!(debug_assertions)`, and authority certificate preparation passes that value into transaction execution. The execution-engine excerpt remains in the existing conservation-check region after gas charging and documents epoch-specific accounting exceptions.

# Root Cause

No confirmed vulnerability root cause is demonstrated by the supplied evidence. The grounded change is that an expensive per-transaction SUI conservation invariant was not shown as configurable in the authority-to-execution path before the patch, and the patch adds explicit configuration plumbing for that check.

## Walkthrough

1. Authority certificate preparation checks inputs, constructs a temporary store, extracts transaction execution parts, and calls transaction execution.

2. Before the patch, the provided call passed epoch data and protocol config but no visible deep per-transaction conservation-check flag.

3. The patch adds `enable_deep_per_tx_sui_conservation_check` to `ExpensiveSafetyCheckConfig` with comments describing input-versus-output SUI accounting, including storage rebate.

4. The patch adds an accessor that enables the check if configured or when debug assertions are enabled.

5. Authority certificate preparation now passes that accessor result into `execute_transaction_to_effects`.

6. The execution-engine context places the relevant logic after gas charging and near existing SUI conservation checks, including comments for epoch rewards, rebates, and unmetered storage rebate.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-adapter/src/execution_engine.rs | 312 | transaction execution path after gas charging where SUI conservation checks are applied |
| crates/sui-config/src/node.rs | 275 | node configuration field controlling deep per-transaction SUI conservation checking |
| crates/sui-config/src/node.rs | 337 | accessor enabling the deep conservation check by config or debug assertions |
| crates/sui-core/src/authority.rs | 987 | authority certificate preparation path passing the configured conservation-check flag into execution |

## Code Snippets

## Snippet 1

Context: `crates/sui-adapter/src/execution_engine.rs:312` (changes the branch that decides whether execution stops or continues)

Before
```rust
let cost_summary =
            temporary_store.charge_gas(gas_object_id, &mut gas_status, &mut result, gas);
         // === begin SUI conservation checks ===
    // For advance epoch transaction, we need to provide epoch rewards and rebates as extra
    // information provided to check_sui_conserved, because we mint rewards, and burn
    // the rebates. We also need to pass in the unmetered_storage_rebate because storage
    // rebate is not reflected in the storage_rebate of gas summary. This is a bit confusing.
    // We could probably clean up the code a bit.
```
After
```rust
let cost_summary =
            temporary_store.charge_gas(gas_object_id, &mut gas_status, &mut result, gas);
        // === begin SUI conservation checks ===
        // For advance epoch transaction, we need to provide epoch rewards and rebates as extra
        // information provided to check_sui_conserved, because we mint rewards, and burn
        // the rebates. We also need to pass in the unmetered_storage_rebate because storage
        // rebate is not reflected in the storage_rebate of gas summary. This is a bit confusing.
        // We could probably clean up the code a bit.
```

## Snippet 2

Context: `crates/sui-config/src/node.rs:275` (changes a sensitive control or state-update path)

Before
```rust
enable_epoch_sui_conservation_check: bool,

    /// Disable epoch SUI conservation check even when we are running in debug mode.
    #[serde(default)]
```
After
```rust
enable_epoch_sui_conservation_check: bool,

    /// If enabled, we will check that the total SUI in all input objects of a tx
    /// (both the Move part and the storage rebate) matches the total SUI in all
    /// output objects of the tx + gas fees
    enable_deep_per_tx_sui_conservation_check: bool,

    /// Disable epoch SUI conservation check even when we are running in debug mode.
```

## Snippet 3

Context: `crates/sui-core/src/authority.rs:987` (changes a sensitive control or state-update path)

Before
```rust
&epoch_store.epoch_start_config().epoch_data(),
                epoch_store.protocol_config(),
            );
```
After
```rust
&epoch_store.epoch_start_config().epoch_data(),
                epoch_store.protocol_config(),
                // TODO: would be nice to pass the whole NodeConfig here, but it creates a
                // cyclic dependency w/ sui-adapter
                self.expensive_safety_check_config
                    .enable_deep_per_tx_sui_conservation_check(),
            );
```

## Snippet 4

Context: `crates/sui-config/src/node.rs:337` (changes a sensitive control or state-update path)

Before
```rust
self.enable_move_vm_paranoid_checks
    }
}
```
After
```rust
self.enable_move_vm_paranoid_checks
    }

    pub fn enable_deep_per_tx_sui_conservation_check(&self) -> bool {
        self.enable_deep_per_tx_sui_conservation_check || cfg!(debug_assertions)
    }
}
```

# Fix Pattern

Add an explicit opt-in expensive invariant guard to node configuration and thread the guard through the transaction execution path, while enabling it automatically in debug builds.

## How It Was Fixed

The patch introduced the `enable_deep_per_tx_sui_conservation_check` node-config field, documented the conservation invariant it controls, added an accessor that also returns true under debug assertions, and passed that value from `AuthorityState` into `execution_engine::execute_transaction_to_effects`.

# Why It Matters

1. Strengthens checks around SUI monetary accounting during transaction execution.

2. Covers both Move-held SUI and storage rebate accounting in the documented invariant.

3. Keeps the expensive validation configurable instead of making it unconditional.

4. Enables the check in debug builds for earlier detection during development and testing.

5. Does not prove a concrete prior exploit or accounting bypass.

# Evidence Notes

Primary evidence comes from `crates/sui-config/src/node.rs`, `crates/sui-core/src/authority.rs`, and the conservation-check region of `crates/sui-adapter/src/execution_engine.rs`. The malformed-transaction parsing, panic-hardening, denial-of-service, and concrete vulnerability-fix narratives are unsupported by the provided evidence. The supplied snippets do not show the full execution-engine signature or the actual conditional use of the new flag, but the authority call and config additions support the configuration-plumbing interpretation. Protocol security invariant: Transaction execution should preserve SUI accounting: total SUI in transaction input objects, including storage rebate, should match total SUI in output objects plus gas fees, with documented epoch-transition exceptions for minted rewards and burned rebates. Verification notes: No concrete pre-patch SUI mint, burn, or accounting bypass is shown. No remote exploitability or denial-of-service condition is proven by the patch evidence. No evidence shows the check is enabled by default in production configurations. The execution_engine excerpt mainly shows the existing conservation-check area; the meaningful behavioral change is the new configuration plumbing. This should not be classified as malformed transaction parsing or panic-hardening based on the provided evidence. No concrete pre-patch SUI mint, burn, or accounting bypass is shown. No remote exploitability or denial-of-service condition is proven. No evidence shows production configurations enable the new check by default. The strongest supported classification is security-relevant hardening, not a confirmed vulnerability fix. Exclude from a vulnerability-fix corpus because the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `monetary-accounting-invariant-hardening`
Final impact type: `asset-integrity`
Final confidence: `medium`
Final tags: `transaction-processing, accounting-invariant, sui-conservation, safety-check, config-hardening`

The supplied evidence supports a security-hardening classification, not a concrete security fix. The patch adds node configuration and authority-to-execution plumbing for an expensive per-transaction SUI conservation check, which is security-relevant because it validates monetary accounting across transaction inputs, outputs, gas fees, and storage rebate. However, the evidence does not prove a pre-existing exploitable bug, production-default enforcement, or a specific way to mint, burn, or bypass accounting incorrectly.

## Security Evidence

1. Commit subject explicitly frames the change as hardening for an expensive per-transaction conservation check.
2. New config field documents checking total SUI in transaction inputs against outputs plus gas fees.
3. Authority execution path now passes the configured deep conservation-check flag into transaction execution.
4. Accessor enables the check when configured or in debug builds.

## Missing Evidence

1. No concrete pre-patch vulnerability or exploit path is shown.
2. No evidence that production nodes enable the check by default.
3. No actual failing transaction, accounting bypass, or supply-inflation scenario is demonstrated.
4. Execution-engine evidence mostly shows surrounding conservation-check comments, not the full conditional enforcement logic.

## Claim Boundaries

1. Classify as security hardening around monetary accounting invariants, not as a confirmed vulnerability fix.
2. Do not claim denial of service, liveness failure, malformed transaction parsing, signature validation, or consensus failure from this evidence.
3. Do not claim production impact unless separate evidence shows the option was enabled in production configurations.
4. The supported impact is conservative asset/accounting integrity risk detection, not proven asset loss.
