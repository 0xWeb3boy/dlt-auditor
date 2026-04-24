# Code-Shape Card

## Metadata

- ID: `geth-arb-2016-11-24-go-ethereum-storage-12d654a6fc`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `consensus-state-divergence`

## Code Shape Summary

- Zero-value account touches were not journaled consistently, so revert and deletion semantics could diverge around empty accounts.

## Search Motifs

- state touch has consensus meaning but is not journaled
- zero-value balance update changes account lifecycle
- revert path omits an account touched during execution
- state cache is keyed by height or alias without canonical hash binding
- lifecycle transition reuses stale progress after reorg or mode switch
- loaded artifact or config is not revalidated against authoritative identity at point of use

## Typical Asymmetry

- The vulnerable asymmetry is stale or incomplete state identity: local lifecycle state could reach state trie commitment and consensus state root without being re-bound to the current authoritative source.

## Patch Pattern

- Record account touches explicitly in the journal and replay/revert them consistently before computing committed state.

## False Match Warnings

- state is invalidated on every relevant reorg, fork, mode, or configuration change
- the sink re-reads authoritative state before use
- the patch only changes cleanup or logging with no acceptance or state-transition effect
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
