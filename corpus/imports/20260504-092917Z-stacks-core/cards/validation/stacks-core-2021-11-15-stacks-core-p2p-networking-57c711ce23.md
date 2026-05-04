# Validation Card

## Metadata

- ID: `stacks-core-2021-11-15-stacks-core-p2p-networking-57c711ce23`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mainnet-consensus-config-hardening`

## What Confirmed The Issue

- Evidence 1: In `testnet/stacks-node/src/burnchains/bitcoin_regtest_controller.rs`, the patch replaces `let burnchain_config = config.burnchain.clone();` with `if network_id == BitcoinNetworkType::Mainnet && config.burnchain.epochs.is_some() {`.
- Evidence 2: In `src/burnchains/bitcoin/indexer.rs`, the patch replaces `fn get_stacks_epochs(&self) -> Vec<StacksEpoch> {` with `///`.

## What Could Have Invalidated It

- Compensating control 1: The value may be used only for display or diagnostics.
- Compensating control 2: Another validation layer may enforce canonical context before finalization.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: The value may be used only for display or diagnostics.
- Caution 2: Another validation layer may enforce canonical context before finalization.
