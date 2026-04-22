---
case_id: case_20260420_88b36d5a2
project: base
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-04-20
source_refs:
  - git:88b36d5a2da9d36361794365005442d7c0a8d155
  - "crates/execution/evm/src/lib.rs:60"
  - "crates/execution/evm/src/lib.rs:398"
  - "crates/execution/evm/src/lib.rs:295"
  - "crates/execution/evm/src/lib.rs:112"
bug_class: missing-runtime-guard
impact_type:
  - policy-bypass
confidence: medium
tags:
  - transaction-processing
  - evm-config
  - gas-limit
  - runtime-guard
  - consensus-rules
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch shows a correctness fix in EVM environment setup: Base V1/Azul-specific `tx_gas_limit_cap` handling was centralized and applied to multiple environment-construction paths. The evidence supports a fork-specific configuration mismatch before the patch, but it does not establish an actual security vulnerability or exploit path.

## Observed Patch Facts

1. In `crates/execution/evm/src/lib.rs`, the patch replaces `/// Builds an ['EvmEnv'] for a given block header using ['base_alloy_evm']'s spec res...` with `fn build_cfg_env(`.

2. In `crates/execution/evm/src/lib.rs`, the patch adds `assert_eq!(cfg_env.tx_gas_limit_cap, Some(MAX_TX_GAS_LIMIT_OSAKA));`.

3. In `crates/execution/evm/src/lib.rs`, the patch replaces `let cfg_env = CfgEnv::new()` with `let cfg_env = build_cfg_env(spec, timestamp, self.chain_spec());`.

4. In `crates/execution/evm/src/lib.rs`, the patch replaces `let cfg_env =` with `let cfg_env = build_cfg_env(spec, attributes.timestamp, chain_spec);`.

## Project Context

The changed code sits primarily in `crates/execution/evm/src`, `crates/execution/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/execution/evm/src/l1.rs`, `crates/execution/evm/src/execute.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/execution/evm/src/l1.rs`, `crates/execution/evm/src/execute.rs`. The strongest project-level identifiers around this patch are `spec`, `cfg_env`, `chain_spec`, and `CfgEnv::new`.

## Before/After Behavior

Before the patch, the shown EVM environment builders constructed `CfgEnv` inline with generic chain/spec parameters and the provided snippets do not show any Base V1-specific `tx_gas_limit_cap` being set in those paths. After the patch, those paths call `build_cfg_env(spec, timestamp, chain_spec)`, which applies `cfg_env.tx_gas_limit_cap = Some(MAX_TX_GAS_LIMIT_OSAKA)` when `is_base_v1_active_at_timestamp(timestamp)` is true, and the test now asserts that behavior under `OpSpecId::BASE_V1`.

# Root Cause

Fork-specific gas-limit policy for Base V1/Azul was omitted from the duplicated inline `CfgEnv` construction paths, so some execution environments could be built without the fork-specific cap even when the timestamp-selected rules were active.

## Walkthrough

1. A new shared helper `build_cfg_env(spec, timestamp, chain_spec)` was introduced to build `CfgEnv` in one place.

2. That helper still sets the normal chain ID and spec-based gas parameters, then additionally checks whether Base V1 is active at the given timestamp.

3. If Base V1 is active, the helper sets `cfg_env.tx_gas_limit_cap = Some(MAX_TX_GAS_LIMIT_OSAKA)`.

4. The `op_next_evm_env(...)` path was changed to use this helper instead of constructing `CfgEnv` inline.

5. The `evm_env_for_payload(...)` path was also changed to use the same helper instead of constructing `CfgEnv` inline.

6. A test was updated to assert both `OpSpecId::BASE_V1` and the expected `tx_gas_limit_cap`, making the intended configuration explicit.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/execution/evm/src/lib.rs | 60 | shared EVM config builder that now applies the Base V1 transaction gas-limit cap |
| crates/execution/evm/src/lib.rs | 112 | next-block EVM environment construction now inherits the capped config |
| crates/execution/evm/src/lib.rs | 289 | payload execution EVM environment now inherits the capped config |
| crates/execution/evm/src/lib.rs | 398 | regression test asserting the cap is present under Base V1 |

## Code Snippets

## Snippet 1

Context: `crates/execution/evm/src/lib.rs:60` (changes a sensitive control or state-update path)

Before
```rust
pub use error::{L1BlockInfoError, OpBlockExecutionError};

/// Builds an [`EvmEnv`] for a given block header using [`base_alloy_evm`]'s spec resolution.
fn op_evm_env(
```
After
```rust
pub use error::{L1BlockInfoError, OpBlockExecutionError};

fn build_cfg_env(
    spec: OpSpecId,
    timestamp: u64,
    chain_spec: &(impl BaseUpgrades + EthChainSpec),
) -> CfgEnv<OpSpecId> {
    let mut cfg_env =
```

## Snippet 2

Context: `crates/execution/evm/src/lib.rs:398` (changes the branch that decides whether execution stops or continues)

Before
```rust
let EvmEnv { cfg_env, .. } = evm_config.evm_env(&header).unwrap();
        assert_eq!(cfg_env.spec, OpSpecId::BASE_V1);
    }
```
After
```rust
let EvmEnv { cfg_env, .. } = evm_config.evm_env(&header).unwrap();
        assert_eq!(cfg_env.spec, OpSpecId::BASE_V1);
        assert_eq!(cfg_env.tx_gas_limit_cap, Some(MAX_TX_GAS_LIMIT_OSAKA));
    }
```

## Snippet 3

Context: `crates/execution/evm/src/lib.rs:295` (changes a sensitive control or state-update path)

Before
```rust
let spec = revm_spec_by_timestamp_after_bedrock(self.chain_spec(), timestamp);

        let cfg_env = CfgEnv::new()
            .with_chain_id(self.chain_spec().chain().id())
            .with_spec_and_mainnet_gas_params(spec);

        let blob_excess_gas_and_price = spec
```
After
```rust
let spec = revm_spec_by_timestamp_after_bedrock(self.chain_spec(), timestamp);
        let cfg_env = build_cfg_env(spec, timestamp, self.chain_spec());

        let blob_excess_gas_and_price = spec
```

## Snippet 4

Context: `crates/execution/evm/src/lib.rs:112` (changes a sensitive control or state-update path)

Before
```rust
) -> EvmEnv<OpSpecId> {
    let spec = revm_spec_by_timestamp_after_bedrock(chain_spec, attributes.timestamp);
    let cfg_env =
        CfgEnv::new().with_chain_id(chain_spec.chain().id()).with_spec_and_mainnet_gas_params(spec);

    let blob_excess_gas_and_price = spec
```
After
```rust
) -> EvmEnv<OpSpecId> {
    let spec = revm_spec_by_timestamp_after_bedrock(chain_spec, attributes.timestamp);
    let cfg_env = build_cfg_env(spec, attributes.timestamp, chain_spec);

    let blob_excess_gas_and_price = spec
```

# Fix Pattern

Centralize duplicated runtime-environment construction and attach fork-conditional parameters in the shared builder, then add a regression test for the fork-specific invariant.

## How It Was Fixed

The fix extracted `CfgEnv` creation into a shared helper and added a Base V1 timestamp check that sets the Osaka gas-limit cap. The previously separate environment-construction paths were updated to call that helper, and regression coverage was added to verify the cap is present for a Base V1 configuration.

# Why It Matters

1. It removes path-dependent configuration differences for the same fork.

2. It makes the Base V1/Azul gas-limit rule explicit and tested.

3. It improves protocol-rule consistency in execution setup.

4. The provided evidence does not show more than a correctness mismatch in configuration handling.

# Evidence Notes

Direct evidence is limited to the shown hunks in `crates/execution/evm/src/lib.rs` and the added assertion in the test. Those hunks support that a Base V1-specific gas-limit cap was previously missing from at least the displayed environment-construction paths and is now applied centrally. The evidence does not prove remote exploitability, consensus failure in production, fund impact, privilege impact, or any concrete attacker-controlled abuse scenario. Protocol security invariant: When Base V1/Azul rules are active for a timestamp, every EVM environment construction path should apply the same fork-specific transaction gas-limit cap. Verification notes: The patch does not prove a remotely exploitable attack path. It is not proven that the pre-patch behavior caused a real consensus split or accepted invalid chain data in production. The evidence does not show fund loss, privilege escalation, or authentication impact. The exact semantics of "implicit gas handling" beyond the missing cap are not fully visible from the provided diff alone. The diff directly shows the new helper setting `tx_gas_limit_cap` under a Base V1 timestamp condition. The diff directly shows two environment-construction paths switching from inline `CfgEnv` creation to the shared helper. The updated test directly verifies the cap is present for a Base V1 configuration. No evidence here demonstrates an actual exploit, incident, or security impact beyond inconsistent fork-specific configuration. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-runtime-guard`
Final impact type: `policy-bypass`
Final confidence: `medium`
Final tags: `transaction-processing, evm-config, gas-limit, runtime-guard, consensus-rules`

The patch is best treated as security hardening rather than a proven vulnerability fix. The code centralizes EVM configuration and adds a fork-conditional `tx_gas_limit_cap` in execution-environment construction paths, which is a security-sensitive runtime guard in transaction processing. That supports retaining it as a hardening example, but the diff alone does not prove exploitability, concrete consensus breakage, or the stronger original "state-corruption" framing.

## Security Evidence

1. A new shared `build_cfg_env` helper sets `cfg_env.tx_gas_limit_cap = Some(MAX_TX_GAS_LIMIT_OSAKA)` when Base V1 is active.
2. Two EVM environment construction paths were changed from inline `CfgEnv` creation to the shared helper, reducing path-dependent omission of the cap.
3. The added test explicitly asserts that `tx_gas_limit_cap` is present for `OpSpecId::BASE_V1`.
4. The changed logic sits in EVM execution environment setup, a security-sensitive transaction-processing path.

## Missing Evidence

1. No evidence shows that pre-patch nodes accepted invalid blocks or transactions in production.
2. No concrete attacker-controlled exploit path or abuse scenario is demonstrated by the diff.
3. No evidence ties the bug to fund loss, privilege gain, authentication bypass, or a confirmed consensus split.
4. The exact external effect of the missing implicit gas handling is not fully visible from the provided patch alone.

## Claim Boundaries

1. The evidence supports a missing fork-specific gas-limit guard in some EVM environment builders.
2. The evidence supports classifying this as security hardening because it tightens a runtime policy in a sensitive execution path.
3. The evidence does not support claiming a confirmed exploitable security bug.
4. The evidence does not support the original stronger labels such as `state-corruption`, `database`, or `signature` impact.
