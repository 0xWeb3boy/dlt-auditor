---
case_id: case_20251229_d9350fcc9
project: base
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2025-12-29
source_refs:
  - git:d9350fcc932ac06f6b1da2846e1261f62cc9a547
  - "crates/op-succinct/fault-proof/src/proposer.rs:1669"
  - "crates/op-succinct/fault-proof/bin/proposer.rs:40"
  - "crates/op-succinct/fault-proof/src/config.rs:132"
  - "crates/op-succinct/fault-proof/src/contract.rs:129"
bug_class: missing-precondition-check
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - fault-proof
  - precondition-check
  - runtime-validation
  - configuration-drift
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a proposer-side guard that skips dispute-game creation when the locally configured game type does not match the chain's currently respected game type. That is a grounded correctness and hardening change in a sensitive path, but the supplied evidence does not establish a concrete vulnerability, exploit path, or downstream security impact from the prior behavior.

## Observed Patch Facts

1. In `crates/op-succinct/fault-proof/src/proposer.rs`, the patch replaces `let (canonical_head_l2_block, parent_game_index) = {` with `// Check if our game type matches the current respected game type.`.

2. In `crates/op-succinct/fault-proof/bin/proposer.rs`, the patch replaces `let l1_provider =` with `let l1_provider = ProviderBuilder::new().connect_http(proposer_config.l1_rpc.clone());`.

3. In `crates/op-succinct/fault-proof/src/config.rs`, the patch adds `anchor_state_registry_address: env::var("ANCHOR_STATE_REGISTRY_ADDRESS")?`.

4. In `crates/op-succinct/fault-proof/src/contract.rs`, the patch adds `/// @notice Returns the respected game type.`.

## Project Context

The changed code sits primarily in `crates/op-succinct/fault-proof/src`, `crates/op-succinct/fault-proof`, `crates/op-succinct/fault-proof/bin`, which anchors the finding in the `storage` area of the project. Historical context from `crates/op-succinct/fault-proof/bin/challenger.rs`, `crates/op-succinct/fault-proof/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/op-succinct/fault-proof/bin/challenger.rs`, `crates/op-succinct/fault-proof/src/lib.rs`. The strongest project-level identifiers around this patch are `env::var`, `parse`, `type`, and `ProviderBuilder::new`. Nearby tests or test-like files include `crates/op-succinct/fault-proof/tests/common/env.rs`, `crates/op-succinct/fault-proof/tests/common/contracts.rs`.

## Before/After Behavior

Before the patch, the proposer creation flow in `crates/op-succinct/fault-proof/src/proposer.rs` continued past earlier checks without first verifying that `self.config.game_type` still matched the registry's current respected game type. After the patch, the proposer calls `self.anchor_state_registry.respectedGameType().call().await?`, compares it to `self.config.game_type`, and if they differ logs a warning and returns early with `Ok((false, U256::ZERO, u32::MAX))`, skipping game creation. Supporting changes add the `respectedGameType()` contract binding, load `ANCHOR_STATE_REGISTRY_ADDRESS` from config, and construct the registry client during proposer startup.

# Root Cause

The proposer relied on local `game_type` configuration without a runtime check against the authoritative on-chain registry state, so it could continue attempting game creation even when local configuration no longer matched the currently respected type.

## Walkthrough

1. `crates/op-succinct/fault-proof/src/proposer.rs` adds a new precondition before game creation: fetch `respectedGameType()` from `self.anchor_state_registry` and compare it to `self.config.game_type`.

2. If the values differ, the proposer logs a warning and returns early instead of continuing the creation flow.

3. `crates/op-succinct/fault-proof/src/contract.rs` adds the `respectedGameType()` method to the `AnchorStateRegistry` binding so the proposer can query that state.

4. `crates/op-succinct/fault-proof/src/config.rs` adds `ANCHOR_STATE_REGISTRY_ADDRESS` to proposer configuration.

5. `crates/op-succinct/fault-proof/bin/proposer.rs` constructs an `AnchorStateRegistry` instance from the configured address and L1 provider, wiring the new check into runtime startup.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/op-succinct/fault-proof/src/proposer.rs | 1669 | Adds pre-create guard that compares proposer `game_type` against `AnchorStateRegistry.respectedGameType()` and aborts creation on mismatch |
| crates/op-succinct/fault-proof/src/contract.rs | 129 | Extends the AnchorStateRegistry contract binding to expose `respectedGameType()` for the guard |
| crates/op-succinct/fault-proof/src/config.rs | 132 | Loads `ANCHOR_STATE_REGISTRY_ADDRESS` so proposer startup can query the live respected game type |
| crates/op-succinct/fault-proof/bin/proposer.rs | 31 | Wires the configured AnchorStateRegistry instance into proposer startup and runtime state |

## Code Snippets

## Snippet 1

Context: `crates/op-succinct/fault-proof/src/proposer.rs:1669` (changes a sensitive control or state-update path)

Before
```rust
}

        let (canonical_head_l2_block, parent_game_index) = {
            let state = self.state.read().await;
```
After
```rust
}

        // Check if our game type matches the current respected game type.
        // The proposer should only create games when its type is the respected type.
        let respected_game_type = self.anchor_state_registry.respectedGameType().call().await?;
        if self.config.game_type != respected_game_type {
            tracing::warn!(
                proposer_game_type = self.config.game_type,
```

## Snippet 2

Context: `crates/op-succinct/fault-proof/bin/proposer.rs:40` (changes the branch that decides whether execution stops or continues)

Before
```rust
let proposer_signer = SignerLock::from_env().await?;

    let l1_provider =
        ProviderBuilder::new().connect_http(env::var("L1_RPC").unwrap().parse::<Url>().unwrap());

    let factory = DisputeGameFactory::new(
        env::var("FACTORY_ADDRESS")
            .expect("FACTORY_ADDRESS must be set")
```
After
```rust
let proposer_signer = SignerLock::from_env().await?;

    let l1_provider = ProviderBuilder::new().connect_http(proposer_config.l1_rpc.clone());

    let anchor_state_registry = AnchorStateRegistry::new(
        proposer_config.anchor_state_registry_address,
        l1_provider.clone(),
    );
```

## Snippet 3

Context: `crates/op-succinct/fault-proof/src/config.rs:132` (changes the branch that decides whether execution stops or continues)

Before
```rust
l1_rpc: env::var("L1_RPC")?.parse().expect("L1_RPC not set"),
            l2_rpc: env::var("L2_RPC")?.parse().expect("L2_RPC not set"),
            factory_address: env::var("FACTORY_ADDRESS")?.parse().expect("FACTORY_ADDRESS not set"),
            mock_mode: env::var("MOCK_MODE").unwrap_or("false".to_string()).parse()?,
```
After
```rust
l1_rpc: env::var("L1_RPC")?.parse().expect("L1_RPC not set"),
            l2_rpc: env::var("L2_RPC")?.parse().expect("L2_RPC not set"),
            anchor_state_registry_address: env::var("ANCHOR_STATE_REGISTRY_ADDRESS")?
                .parse()
                .expect("ANCHOR_STATE_REGISTRY_ADDRESS not set"),
            factory_address: env::var("FACTORY_ADDRESS")?.parse().expect("FACTORY_ADDRESS not set"),
            mock_mode: env::var("MOCK_MODE").unwrap_or("false".to_string()).parse()?,
```

## Snippet 4

Context: `crates/op-succinct/fault-proof/src/contract.rs:129` (changes a sensitive control or state-update path)

Before
```rust
/// @notice Returns the current anchor game reference.
        function anchorGame() public view returns (IDisputeGame anchorGame_);
    }
```
After
```rust
/// @notice Returns the current anchor game reference.
        function anchorGame() public view returns (IDisputeGame anchorGame_);

        /// @notice Returns the respected game type.
        function respectedGameType() external view returns (GameType);
    }
```

# Fix Pattern

Add a runtime precondition check against authoritative on-chain state immediately before a side-effecting operation, and abort when local configuration disagrees with that state.

## How It Was Fixed

The proposer was updated to query `AnchorStateRegistry` for the current respected game type and refuse to create a game on mismatch. The patch also added the contract binding and configuration/runtime plumbing needed to perform that check.

# Why It Matters

1. Prevents the proposer from creating games under a locally configured type that is no longer the respected type.

2. Reduces stale-configuration or upgrade-mismatch behavior in the game-creation path.

3. Makes the proposer enforce an explicit runtime invariant instead of assuming configuration remains correct.

4. The available evidence supports correctness hardening, not a demonstrated exploitable break.

# Evidence Notes

The strongest evidence is the new early-return guard in `crates/op-succinct/fault-proof/src/proposer.rs`, supported by the added `respectedGameType()` binding in `crates/op-succinct/fault-proof/src/contract.rs` and the new `ANCHOR_STATE_REGISTRY_ADDRESS` plumbing in config and startup. The provided excerpts do not show a contract-side acceptance flaw, an attacker-controlled path, or concrete impact such as fund loss, privilege bypass, or consensus failure. Because the security thesis is not established by the supplied code evidence, this should remain classified as `unclear` and excluded from the security corpus. Protocol security invariant: The proposer should only create dispute games when its configured `game_type` matches the live `respectedGameType` returned by `AnchorStateRegistry`. The patch enforces that invariant in proposer-side logic, but the provided evidence does not show what happens on-chain if the proposer fails to do so. Verification notes: The patch does not prove that an attacker could force creation of a malicious game type. The patch does not show that unrespected games would be accepted by on-chain settlement or anchoring logic. The evidence does not establish fund loss, privilege bypass, or consensus compromise. The change may primarily prevent stale-config or upgrade-mismatch behavior rather than fix an exploitable vulnerability. Evidence directly shows a new proposer-side guard on game-type mismatch. Evidence supports `missing-precondition-check` more than storage corruption or stronger security classes. No supplied excerpt shows how unrespected games would be handled downstream or on-chain. Commit metadata mentions tests, but no test excerpt here proves a security regression scenario. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-precondition-check`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, fault-proof, precondition-check, runtime-validation, configuration-drift`

The patch adds a new runtime guard in a security-sensitive dispute-game creation path: before creating a game, the proposer now queries the authoritative on-chain registry for the currently respected game type and aborts on mismatch. That is stronger than a pure reliability refactor because it prevents a side-effecting operation from proceeding under stale or inconsistent configuration in a protocol-critical workflow. The evidence still does not prove a concrete exploitable vulnerability or downstream acceptance of a bad game, so this is best retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. `proposer.rs` adds an explicit precondition check against `anchor_state_registry.respectedGameType()` immediately before game creation.
2. On mismatch, the proposer logs a warning and returns early, skipping the side-effecting create path.
3. `contract.rs` adds the `respectedGameType()` binding, showing the check is against live on-chain state rather than only local config.
4. `config.rs` and `bin/proposer.rs` add registry-address plumbing needed to enforce the new validation at runtime.
5. The guarded operation is dispute-game creation, which is a protocol-sensitive path rather than ordinary application logic.

## Missing Evidence

1. No supplied excerpt shows that unrespected games would previously be accepted on-chain or could affect settlement.
2. No attacker-controlled input or exploit sequence is demonstrated in the provided patch evidence.
3. No evidence shows concrete impact such as fund loss, privilege gain, or consensus failure.
4. No test excerpt is provided that demonstrates a security regression scenario rather than a correctness mismatch.

## Claim Boundaries

1. The patch proves a missing runtime validation was added before creating dispute games.
2. The patch supports classifying the change as security hardening in a sensitive blockchain path.
3. The patch does not by itself prove an exploitable vulnerability existed before the change.
4. The evidence does not support stronger labels such as state corruption, privilege bypass, or confirmed consensus compromise.
