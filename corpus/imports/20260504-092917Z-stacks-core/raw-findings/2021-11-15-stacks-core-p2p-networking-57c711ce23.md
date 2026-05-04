---
case_id: case_20211115_57c711ce23
project: stacks-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: p2p-networking
source_quality: high
date: 2021-11-15
source_refs:
  - git:57c711ce235d7c5e854a2c8ef9329963b42fbdda
  - "testnet/stacks-node/src/burnchains/bitcoin_regtest_controller.rs:220"
  - "src/burnchains/bitcoin/indexer.rs:707"
  - "testnet/stacks-node/src/config.rs:487"
  - "testnet/stacks-node/src/config.rs:923"
bug_class: mainnet-consensus-config-hardening
impact_type:
  - consensus-integrity
  - configuration-integrity
confidence: medium
tags:
  - blockchain-core
  - burnchain
  - configuration
  - consensus
  - mainnet-safety
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds support for TOML-supplied burnchain epochs and adds guards to reject custom epochs on Mainnet. The evidence supports a configuration safety boundary for a new testnet/regtest feature, but it does not establish that a pre-existing vulnerability was reachable or exploitable.

## Observed Patch Facts

1. In `testnet/stacks-node/src/burnchains/bitcoin_regtest_controller.rs`, the patch replaces `let burnchain_config = config.burnchain.clone();` with `if network_id == BitcoinNetworkType::Mainnet && config.burnchain.epochs.is_some() {`.

2. In `src/burnchains/bitcoin/indexer.rs`, the patch replaces `fn get_stacks_epochs(&self) -> Vec<StacksEpoch> {` with `///`.

3. In `testnet/stacks-node/src/config.rs`, the patch replaces `epochs: default_burnchain_config.epochs,` with `epochs: match burnchain.epochs {`.

4. In `testnet/stacks-node/src/config.rs`, the patch adds `/// Custom override for the definitions of the epochs. This will only be applied for...`.

## Project Context

The changed code sits primarily in `testnet/stacks-node/src/burnchains`, `testnet/stacks-node/src`, `src/burnchains/bitcoin`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `testnet/stacks-node/src/node.rs`, `src/burnchains/bitcoin/spv.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `testnet/stacks-node/src/node.rs`, `src/burnchains/bitcoin/spv.rs`. The strongest project-level identifiers around this patch are `epochs`, `BitcoinNetworkType::Mainnet`, `burnchain`, and `config`. Nearby tests or test-like files include `testnet/stacks-node/src/tests/neon_integrations.rs`, `testnet/stacks-node/src/tests/integrations.rs`.

## Before/After Behavior

Before the patch, the testnet configuration merge path ignored TOML-supplied burnchain.epochs and used default_burnchain_config.epochs. The Bitcoin indexer selected configured epochs when present, otherwise falling back to hard-coded epochs, with no shown Mainnet assertion in that branch. After the patch, TOML-supplied epochs are preserved, the regtest controller panics if custom epochs are configured while network_id is Mainnet, and the indexer asserts that configured epochs are not used on Mainnet.

# Root Cause

The supported issue is that a new custom-epoch configuration path needed an explicit Mainnet boundary. The evidence does not prove that Mainnet nodes could previously be driven into non-canonical epoch selection through TOML configuration, because the prior config merge path shown ignored TOML-supplied epochs.

## Walkthrough

1. Configuration merging in testnet/stacks-node/src/config.rs now preserves burnchain.epochs when supplied.

2. BurnchainConfig documentation now says custom epoch overrides apply only for testnet and regtest nodes.

3. bitcoin_regtest_controller.rs adds an early panic when network_id is Mainnet and config.burnchain.epochs is set.

4. bitcoin/indexer.rs adds an assertion before returning configured epochs that runtime.network_id is not Mainnet.

5. No evidence shows remote attacker control, malformed epoch validation, or a demonstrated Mainnet consensus failure before this patch.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| testnet/stacks-node/src/burnchains/bitcoin_regtest_controller.rs | 220 | early runtime guard panicking if custom burnchain epochs are configured while network_id is Mainnet |
| src/burnchains/bitcoin/indexer.rs | 707 | epoch schedule selection path that uses configured epochs only after asserting the runtime network is not Mainnet |
| testnet/stacks-node/src/config.rs | 487 | configuration merge path that preserves TOML-supplied burnchain epochs instead of always using defaults |
| testnet/stacks-node/src/config.rs | 923 | BurnchainConfig field documenting custom epochs as testnet/regtest-only |

## Code Snippets

## Snippet 1

Context: `testnet/stacks-node/src/burnchains/bitcoin_regtest_controller.rs:220` (changes a consensus- or validator-sensitive branch)

Before
```rust
.expect("Bitcoin network unsupported");

        let indexer_config = {
            let burnchain_config = config.burnchain.clone();
```
After
```rust
.expect("Bitcoin network unsupported");

        if network_id == BitcoinNetworkType::Mainnet && config.burnchain.epochs.is_some() {
            panic!("It is an error to set custom epochs while running on Mainnet: network_id {:?} config.burnchain {:#?}",
                   &network_id, &config.burnchain);
        }

        let indexer_config = {
```

## Snippet 2

Context: `src/burnchains/bitcoin/indexer.rs:707` (changes a consensus- or validator-sensitive branch)

Before
```rust
/// Get a vector of the stacks epochs. This notion of epochs is dependent on the burn block height.
    /// Valid epochs include stacks 1.0, stacks 2.0, stacks 2.05, and so on.
    fn get_stacks_epochs(&self) -> Vec<StacksEpoch> {
        match self.config.epochs {
            Some(ref epochs) => epochs.clone(),
            None => get_bitcoin_stacks_epochs(self.runtime.network_id),
        }
```
After
```rust
/// Get a vector of the stacks epochs. This notion of epochs is dependent on the burn block height.
    /// Valid epochs include stacks 1.0, stacks 2.0, stacks 2.05, and so on.
    ///
    /// Choose according to:
    /// 1) Use the custom epochs defined on the underlying `BitcoinIndexerConfig`, if they exist.
    /// 2) Use hard-coded static values, otherwise.
    ///
    /// It is an error (panic) to set custom epochs if running on `Mainnet`.
```

## Snippet 3

Context: `testnet/stacks-node/src/config.rs:487` (changes a consensus- or validator-sensitive branch)

Before
```rust
.rbf_fee_increment
                        .unwrap_or(default_burnchain_config.rbf_fee_increment),
                    epochs: default_burnchain_config.epochs,
                }
            }
```
After
```rust
.rbf_fee_increment
                        .unwrap_or(default_burnchain_config.rbf_fee_increment),
                    epochs: match burnchain.epochs {
                        Some(epochs) => Some(epochs),
                        None => default_burnchain_config.epochs,
                    },
                }
            }
```

## Snippet 4

Context: `testnet/stacks-node/src/config.rs:923` (changes a sensitive control or state-update path)

Before
```rust
pub block_commit_tx_estimated_size: u64,
    pub rbf_fee_increment: u64,
    pub epochs: Option<Vec<StacksEpoch>>,
}
```
After
```rust
pub block_commit_tx_estimated_size: u64,
    pub rbf_fee_increment: u64,
    /// Custom override for the definitions of the epochs. This will only be applied for testnet and
    /// regtest nodes.
    pub epochs: Option<Vec<StacksEpoch>>,
}
```

# Fix Pattern

Introduce configurable testnet/regtest behavior while adding explicit guards that prevent the same configuration from being used on Mainnet.

## How It Was Fixed

The patch preserved TOML-supplied epochs during configuration merging, documented the field as testnet/regtest-only, added an early Mainnet rejection in controller setup, and added a downstream assertion in the indexer epoch-selection branch.

# Why It Matters

1. Custom epoch schedules can affect consensus activation behavior.

2. Mainnet should use canonical hard-coded epoch definitions.

3. The patch reduces risk from a newly exposed configuration option.

4. The evidence does not establish a vulnerability fix.

# Evidence Notes

The mapper's p2p-networking and state-corruption framing is unsupported. The grounded subsystem is burnchain configuration and epoch selection. The claim that this fixed an exploitable vulnerability is not established: the shown pre-patch configuration merge ignored TOML epochs, and no attacker path or prior Mainnet misconfiguration path is proven. Protocol security invariant: Mainnet nodes should not run with operator-supplied custom Stacks epoch schedules; custom epoch configuration is intended only for testnet or regtest. Verification notes: The patch does not prove a remote attacker can modify node configuration. The patch does not show that mainnet defaults were wrong before this commit. The patch does not show validation of custom epoch contents beyond disallowing them on Mainnet. The patch does not establish a p2p-networking vulnerability. The evidence supports consensus-configuration hardening, not confirmed exploitability. Supported by hunks in testnet/stacks-node/src/config.rs, bitcoin_regtest_controller.rs, and src/burnchains/bitcoin/indexer.rs. No tests or exploit scenario are provided in the input. Classified as unclear rather than likely security because the patch appears to safely add a feature, not demonstrably fix an existing vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `mainnet-consensus-config-hardening`
Final impact type: `consensus-integrity, configuration-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, burnchain, configuration, consensus, mainnet-safety, hardening`

The patch does not prove an exploitable vulnerability or a pre-existing reachable Mainnet consensus bug, because the shown pre-patch merge path ignored TOML-supplied epochs. However, it does add explicit Mainnet rejection and a downstream assertion around custom epoch schedules, which are consensus-sensitive and documented as testnet/regtest-only. This supports retaining the case as security hardening, not as a confirmed security fix, and the original p2p/state-corruption framing should be narrowed.

## Security Evidence

1. Adds an early panic when network_id is Mainnet and custom burnchain epochs are configured.
2. Adds an assertion before returning configured epochs from the Bitcoin indexer on Mainnet.
3. Documents custom epoch overrides as only applying to testnet and regtest nodes.
4. Epoch schedules affect consensus activation behavior, making the boundary security-sensitive.

## Missing Evidence

1. No evidence of remote attacker control over node configuration.
2. No evidence that TOML-supplied epochs affected Mainnet before this patch; the shown merge path previously ignored them.
3. No exploit scenario, test failure, advisory, or demonstrated consensus divergence is provided.
4. No validation of malformed custom epoch contents is shown beyond disallowing Mainnet use.

## Claim Boundaries

1. Classify as consensus-configuration hardening, not a confirmed vulnerability fix.
2. Do not claim p2p-networking exposure from the supplied evidence.
3. Do not claim state corruption or remote exploitability.
4. Do not claim Mainnet was previously vulnerable to TOML epoch override without additional evidence.
