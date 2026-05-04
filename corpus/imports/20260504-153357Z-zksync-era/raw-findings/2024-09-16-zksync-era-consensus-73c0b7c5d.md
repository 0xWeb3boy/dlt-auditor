---
case_id: case_20240916_73c0b7c5d
project: zksync-era
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2024-09-16
source_refs:
  - git:73c0b7c5d7f8f156657fd1c9ed502cc2fff7e063
  - "zk_toolbox/crates/zk_inception/src/commands/chain/deploy_paymaster.rs:56"
  - "zk_toolbox/crates/zk_inception/src/commands/chain/init.rs:21"
  - "zk_toolbox/crates/zk_inception/src/commands/ecosystem/init.rs:274"
  - "zk_toolbox/crates/zk_inception/src/messages.rs:123"
bug_class: key-management-hardening
impact_type:
  - private-key-exposure-reduction
  - unsafe-broadcast-risk-reduction
confidence: medium
tags:
  - blockchain-tooling
  - deployment-tooling
  - key-management
  - cold-storage
  - multisig
  - unsigned-transactions
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence shows a new zk_toolbox workflow for building unsigned L1 deployment transactions and related Forge setup changes that allow an explicit sender address instead of immediately using a private key in the shown path. This is security-relevant operational hardening for cold-storage or multisig signing. The evidence does not prove a prior private-key leak, unauthorized broadcast path, consensus issue, validator issue, or accounting/state-drift vulnerability.

## Observed Patch Facts

1. In `zk_toolbox/crates/zk_inception/src/commands/chain/deploy_paymaster.rs`, the patch replaces `.with_broadcast();` with `);`.

2. In `zk_toolbox/crates/zk_inception/src/commands/chain/init.rs`, the patch replaces `consts::AMOUNT_FOR_DISTRIBUTION_TO_WALLETS,` with `MSG_CHAIN_NOT_FOUND_ERR, MSG_DEPLOYING_PAYMASTER, MSG_GENESIS_DATABASE_ERR,`.

3. In `zk_toolbox/crates/zk_inception/src/commands/ecosystem/init.rs`, the patch replaces `let deploy_config_path = DEPLOY_ECOSYSTEM_SCRIPT_PARAMS.input(&config.link_to_code);` with `let spinner = Spinner::new(MSG_DEPLOYING_ECOSYSTEM_CONTRACTS_SPINNER);`.

4. In `zk_toolbox/crates/zk_inception/src/messages.rs`, the patch replaces `/// Chain create related messages` with `/// Build ecosystem transactions related messages`.

## Project Context

The changed code sits primarily in `zk_toolbox/crates/zk_inception/src/commands/chain`, `zk_toolbox/crates/zk_inception/src/commands`, `zk_toolbox/crates/zk_inception/src/commands/ecosystem`, which anchors the finding in the `consensus` area of the project. Historical context from `zk_toolbox/crates/zk_inception/src/commands/ecosystem/build_transactions.rs`, `zk_toolbox/crates/zk_inception/src/commands/chain/build_transactions.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `zk_toolbox/crates/zk_inception/src/commands/ecosystem/build_transactions.rs`, `zk_toolbox/crates/zk_inception/src/commands/chain/build_transactions.rs`. The strongest project-level identifiers around this patch are `forge`, `super`, `const`, and `ecosystem`.

## Before/After Behavior

Before the change, the shown paymaster deployment Forge setup chained `.with_broadcast()` and then proceeded through private-key filling for the governor key path. After the change, the shown setup no longer includes `.with_broadcast()` at that point and branches on an optional sender address, using `forge.with_sender(address)` when supplied and falling back to `fill_forge_private_key(...)` otherwise. The commit also adds ecosystem and chain `build-transactions` command paths and messages for writing unsigned transaction output.

# Root Cause

No vulnerability root cause is established by the supplied evidence. The supported issue is an operational limitation: deployment tooling was oriented around private-key-backed signing and broadcasting, while the new workflow supports unsigned transaction construction for external cold-storage or multisig signing.

## Walkthrough

1. The commit message says the new subcommands build L1 transactions without signing and broadcasting them so a security team can sign using cold storage and multisig.

2. The shown `deploy_paymaster` diff removes `.with_broadcast()` from the displayed Forge construction snippet.

3. The function now accepts a sender option and uses `forge.with_sender(address)` when a sender is supplied.

4. When no sender is supplied, the shown path continues to use `fill_forge_private_key(...)`.

5. New ecosystem and chain `build_transactions` command paths are included in the changed files and traced context.

6. New messages describe building ecosystem transactions and writing output files.

7. None of the provided evidence demonstrates an exploitable vulnerability in the previous behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| zk_toolbox/crates/zk_inception/src/commands/chain/deploy_paymaster.rs | 56 | switches paymaster deployment forge setup between unsigned sender-based construction and private-key-backed broadcast/signing behavior |
| zk_toolbox/crates/zk_inception/src/commands/ecosystem/build_transactions.rs | 1 | new ecosystem transaction-building command path for unsigned deployment transaction output |
| zk_toolbox/crates/zk_inception/src/commands/chain/build_transactions.rs | 1 | new chain registration transaction-building command path for unsigned transaction output |
| zk_toolbox/crates/zk_inception/src/commands/ecosystem/init.rs | 274 | refactors ecosystem deployment internals through shared deploy_l1 flow used by build/deploy paths |
| zk_toolbox/crates/zk_inception/src/messages.rs | 123 | adds user-facing messages for transaction-building workflow |

## Code Snippets

## Snippet 1

Context: `zk_toolbox/crates/zk_inception/src/commands/chain/deploy_paymaster.rs:56` (updates aggregate accounting or lifecycle state)

Before
```rust
.expose_str()
                .to_string(),
        )
        .with_broadcast();

    forge = fill_forge_private_key(
        forge,
        chain_config.get_wallets_config()?.governor_private_key(),
```
After
```rust
.expose_str()
                .to_string(),
        );

    if let Some(address) = sender {
        forge = forge.with_sender(address);
    } else {
        forge = fill_forge_private_key(
```

## Snippet 2

Context: `zk_toolbox/crates/zk_inception/src/commands/chain/init.rs:21` (updates aggregate accounting or lifecycle state)

Before
```rust
portal::update_portal_config,
    },
    consts::AMOUNT_FOR_DISTRIBUTION_TO_WALLETS,
    messages::{
        msg_initializing_chain, MSG_ACCEPTING_ADMIN_SPINNER, MSG_CHAIN_INITIALIZED,
        MSG_CHAIN_NOT_FOUND_ERR, MSG_DISTRIBUTING_ETH_SPINNER, MSG_GENESIS_DATABASE_ERR,
        MSG_MINT_BASE_TOKEN_SPINNER, MSG_PORTAL_FAILED_TO_CREATE_CONFIG_ERR, MSG_PORTS_CONFIG_ERR,
        MSG_REGISTERING_CHAIN_SPINNER, MSG_SELECTED_CONFIG,
```
After
```rust
portal::update_portal_config,
    },
    messages::{
        msg_initializing_chain, MSG_ACCEPTING_ADMIN_SPINNER, MSG_CHAIN_INITIALIZED,
        MSG_CHAIN_NOT_FOUND_ERR, MSG_DEPLOYING_PAYMASTER, MSG_GENESIS_DATABASE_ERR,
        MSG_PORTAL_FAILED_TO_CREATE_CONFIG_ERR, MSG_PORTS_CONFIG_ERR,
        MSG_REGISTERING_CHAIN_SPINNER, MSG_SELECTED_CONFIG,
        MSG_UPDATING_TOKEN_MULTIPLIER_SETTER_SPINNER, MSG_WALLET_TOKEN_MULTIPLIER_SETTER_NOT_FOUND,
```

## Snippet 3

Context: `zk_toolbox/crates/zk_inception/src/commands/ecosystem/init.rs:274` (updates aggregate accounting or lifecycle state)

Before
```rust
l1_rpc_url: String,
) -> anyhow::Result<ContractsConfig> {
    let deploy_config_path = DEPLOY_ECOSYSTEM_SCRIPT_PARAMS.input(&config.link_to_code);

    let default_genesis_config =
        GenesisConfig::read_with_base_path(shell, config.get_default_configs_path())
            .context("Context")?;
```
After
```rust
l1_rpc_url: String,
) -> anyhow::Result<ContractsConfig> {
    let spinner = Spinner::new(MSG_DEPLOYING_ECOSYSTEM_CONTRACTS_SPINNER);
    let contracts_config = deploy_l1(
        shell,
        &forge_args,
        config,
        initial_deployment_config,
```

## Snippet 4

Context: `zk_toolbox/crates/zk_inception/src/messages.rs:123` (updates aggregate accounting or lifecycle state)

Before
```rust
}

/// Chain create related messages
pub(super) const MSG_PROVER_MODE_HELP: &str = "Prover options";
```
After
```rust
}

/// Build ecosystem transactions related messages
pub(super) const MSG_SENDER_ADDRESS_PROMPT: &str = "What is the address of the transaction sender?";
pub(super) const MSG_BUILDING_ECOSYSTEM: &str = "Building ecosystem transactions";
pub(super) const MSG_BUILDING_ECOSYSTEM_CONTRACTS_SPINNER: &str = "Building ecosystem contracts...";
pub(super) const MSG_WRITING_OUTPUT_FILES_SPINNER: &str = "Writing output files...";
pub(super) const MSG_ECOSYSTEM_TXN_OUTRO: &str = "Transactions successfully built";
```

# Fix Pattern

Add an offline transaction-building mode that separates transaction construction from signing and broadcasting, while preserving private-key-backed behavior for paths that still require it.

## How It Was Fixed

The patch adds `zki ecosystem build-transactions` and `zki chain build-transactions` paths for unsigned transaction output. It adjusts Forge setup in the shown paymaster deployment path so an explicit sender address can be used for transaction construction without immediately filling a private key in that branch, and it factors ecosystem deployment through shared transaction construction behavior.

# Why It Matters

1. Supports cold-storage or multisig signing for privileged L1 deployment transactions.

2. Reduces dependence on hot-key signing during transaction construction when a sender address is supplied.

3. Improves separation between building, signing, and broadcasting deployment transactions.

4. Does not establish a prior exploitable vulnerability from the supplied evidence.

# Evidence Notes

Grounded evidence comes from the commit message, changed files, and shown snippets in `deploy_paymaster.rs`, ecosystem and chain `build_transactions` command paths, `deploy_ecosystem_inner`, and transaction-building messages. The heuristic baseline's consensus accounting/state-drift narrative is unsupported and should be discarded. The evidence supports security hardening, not a confirmed vulnerability fix. Protocol security invariant: Privileged L1 deployment transactions should be constructible separately from signing and broadcasting when an offline cold-storage or multisig signing workflow is required. The evidence supports an operational key-management improvement, but does not establish that the previous behavior violated a protocol security invariant or created an exploitable vulnerability. Verification notes: No evidence shows a prior private-key leak. No evidence shows unauthorized transaction broadcast was possible before this patch. No exploit path against consensus, validators, or chain state is proven. No aggregate accounting or state-drift bug is supported by the shown diff. This appears to add an offline signing workflow rather than fix a concrete vulnerability. No evidence of private-key disclosure is provided. No evidence of unauthorized broadcast is provided. No consensus, validator, or chain-state exploit path is shown. No accounting or aggregate state drift issue is supported by the supplied diff context. Keep out of a vulnerability-fix corpus unless additional evidence proves a concrete prior vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `key-management-hardening`
Final impact type: `private-key-exposure-reduction, unsafe-broadcast-risk-reduction`
Final confidence: `medium`
Final tags: `blockchain-tooling, deployment-tooling, key-management, cold-storage, multisig, unsigned-transactions`

The supplied evidence does not support a consensus, accounting, state-drift, validator, or concrete vulnerability-fix finding. It does support security hardening: the commit explicitly adds unsigned transaction-building workflows so privileged L1 deployment transactions can be signed via cold storage or multisig, and the shown Forge setup removes immediate broadcast behavior and allows a sender address path without filling a private key.

## Security Evidence

1. Commit states transactions are built without signing and broadcasting.
2. Commit states the workflow allows security teams to sign using cold storage and multisig.
3. Patch removes `.with_broadcast()` from the shown Forge setup path.
4. Patch adds sender-address handling before falling back to private-key filling.
5. New build-transactions command paths output unsigned deployment transactions.

## Missing Evidence

1. No evidence of prior private-key leakage.
2. No evidence of unauthorized transaction broadcast before the patch.
3. No exploit path against consensus, validators, or chain state is shown.
4. No accounting or state-drift bug is supported by the snippets.

## Claim Boundaries

1. Validate only as operational key-management hardening.
2. Do not classify as a concrete security vulnerability fix.
3. Do not retain the original consensus or accounting/state-drift classification.
4. Do not claim impact beyond reducing hot-key signing and broadcast exposure for deployment workflows.
