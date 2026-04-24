# Code-Shape Card

## Metadata

- ID: `geth-arb-2024-12-20-go-ethereum-transaction-processing-a719c5c923`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `hardening-or-correctness-fix`

## Code Shape Summary

- The sequencer admission loop needed to keep processing only while the authoritative round still matched the submitted message round.

## Search Motifs

- privileged submission loop checks sender but not current round
- round-scoped message accepted after round changed
- cached round state not compared at sequencing sink
- state cache is keyed by height or alias without canonical hash binding
- lifecycle transition reuses stale progress after reorg or mode switch
- loaded artifact or config is not revalidated against authoritative identity at point of use

## Typical Asymmetry

- The vulnerable asymmetry is stale or incomplete state identity: local lifecycle state could reach round-specific sequencing or express-lane acceptance without being re-bound to the current authoritative source.

## Patch Pattern

- Add the round equality condition to the processing loop so stale or cross-round messages stop before sequencing.

## False Match Warnings

- state is invalidated on every relevant reorg, fork, mode, or configuration change
- the sink re-reads authoritative state before use
- the patch only changes cleanup or logging with no acceptance or state-transition effect
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
