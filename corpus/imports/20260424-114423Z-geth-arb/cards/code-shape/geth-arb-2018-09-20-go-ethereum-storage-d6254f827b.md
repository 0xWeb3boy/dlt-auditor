# Code-Shape Card

## Metadata

- ID: `geth-arb-2018-09-20-go-ethereum-storage-d6254f827b`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `fork-choice-tie-break-hardening`

## Code Shape Summary

- Equal-difficulty same-height blocks could trigger random reorg behavior instead of preferentially retaining the local canonical block.

## Search Motifs

- fork choice uses randomness for equal weight blocks
- same-height same-work competitor can trigger reorg churn
- tie-break ignores local canonical preference
- state cache is keyed by height or alias without canonical hash binding
- lifecycle transition reuses stale progress after reorg or mode switch
- loaded artifact or config is not revalidated against authoritative identity at point of use

## Typical Asymmetry

- The vulnerable asymmetry is stale or incomplete state identity: local lifecycle state could reach canonical-chain selection and reorg execution without being re-bound to the current authoritative source.

## Patch Pattern

- Replace random tie-breaking with deterministic local-chain preference when total difficulty and height are equal.

## False Match Warnings

- state is invalidated on every relevant reorg, fork, mode, or configuration change
- the sink re-reads authoritative state before use
- the patch only changes cleanup or logging with no acceptance or state-transition effect
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
