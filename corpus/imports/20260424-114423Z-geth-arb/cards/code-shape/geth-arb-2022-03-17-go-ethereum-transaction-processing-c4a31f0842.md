# Code-Shape Card

## Metadata

- ID: `geth-arb-2022-03-17-go-ethereum-transaction-processing-c4a31f0842`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `validator-reorg-state-mismatch`

## Code Shape Summary

- Validator state tracked the last validated height without sufficiently binding it to the block hash, allowing stale progress to survive an L2 reorg at the same height.

## Search Motifs

- validator progress keyed by height only
- same-height reorg does not invalidate cached validation state
- node action generated from stale canonical-chain identity
- state cache is keyed by height or alias without canonical hash binding
- lifecycle transition reuses stale progress after reorg or mode switch
- loaded artifact or config is not revalidated against authoritative identity at point of use

## Typical Asymmetry

- The vulnerable asymmetry is stale or incomplete state identity: local lifecycle state could reach validator progress continuation and L1 node-action generation without being re-bound to the current authoritative source.

## Patch Pattern

- Persist and compare the validated block hash with live canonical state, and stop progress when the stored hash mismatches.

## False Match Warnings

- state is invalidated on every relevant reorg, fork, mode, or configuration change
- the sink re-reads authoritative state before use
- the patch only changes cleanup or logging with no acceptance or state-transition effect
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
