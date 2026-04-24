# Code-Shape Card

## Metadata

- ID: `geth-arb-2017-08-25-go-ethereum-storage-08f27428b4`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `contract-address-collision-prevention`

## Code Shape Summary

- The CREATE path needed an explicit occupied-account check so deployment could not overwrite or collide with existing nonce/code state under the fork rule.

## Search Motifs

- contract creation computes address but does not check existing nonce/code
- fork rule adds collision semantics not enforced in EVM path
- code installation can proceed on an occupied account
- state cache is keyed by height or alias without canonical hash binding
- lifecycle transition reuses stale progress after reorg or mode switch
- loaded artifact or config is not revalidated against authoritative identity at point of use

## Typical Asymmetry

- The vulnerable asymmetry is stale or incomplete state identity: local lifecycle state could reach new contract account creation and code installation without being re-bound to the current authoritative source.

## Patch Pattern

- Compute the destination address before creation, check nonce and code hash, and return a collision error before code installation.

## False Match Warnings

- state is invalidated on every relevant reorg, fork, mode, or configuration change
- the sink re-reads authoritative state before use
- the patch only changes cleanup or logging with no acceptance or state-transition effect
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
