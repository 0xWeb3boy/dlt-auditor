# Code-Shape Card

## Metadata

- ID: `geth-arb-2022-04-10-go-ethereum-transaction-processing-3a9ee37539`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `module-root-validation-hardening`

## Code Shape Summary

- Machine loading mixed latest-root aliases with explicit module-root requests and needed to verify the loaded machine reported the expected root.

## Search Motifs

- artifact alias resolved without final identity check
- loaded VM reports root but caller does not compare it
- latest pointer and explicit root share acceptance path
- state cache is keyed by height or alias without canonical hash binding
- lifecycle transition reuses stale progress after reorg or mode switch
- loaded artifact or config is not revalidated against authoritative identity at point of use

## Typical Asymmetry

- The vulnerable asymmetry is stale or incomplete state identity: local lifecycle state could reach accepted execution machine for validation or staking without being re-bound to the current authoritative source.

## Patch Pattern

- Canonicalize aliases first, then compare the loaded artifact root to the requested root before assigning the machine.

## False Match Warnings

- state is invalidated on every relevant reorg, fork, mode, or configuration change
- the sink re-reads authoritative state before use
- the patch only changes cleanup or logging with no acceptance or state-transition effect
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
