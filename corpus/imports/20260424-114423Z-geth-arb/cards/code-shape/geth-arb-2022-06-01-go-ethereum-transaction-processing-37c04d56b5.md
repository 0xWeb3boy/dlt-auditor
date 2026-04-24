# Code-Shape Card

## Metadata

- ID: `geth-arb-2022-06-01-go-ethereum-transaction-processing-37c04d56b5`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `hardening-or-correctness-fix`

## Code Shape Summary

- The withdrawal path was hardened by removing configurable withdrawal destinations from the staker flow and relying on the privileged sink to use its trusted destination semantics.

## Search Motifs

- withdrawal sink accepts destination from caller path
- privileged fund movement takes address parameter that can be removed
- safer fix narrows API rather than validating late
- state cache is keyed by height or alias without canonical hash binding
- lifecycle transition reuses stale progress after reorg or mode switch
- loaded artifact or config is not revalidated against authoritative identity at point of use

## Typical Asymmetry

- The vulnerable asymmetry is stale or incomplete state identity: local lifecycle state could reach withdrawal of staker funds to a destination address without being re-bound to the current authoritative source.

## Patch Pattern

- Narrow the sensitive sink signature by removing caller-controlled destination input and route withdrawals through the fixed trusted-destination helper.

## False Match Warnings

- state is invalidated on every relevant reorg, fork, mode, or configuration change
- the sink re-reads authoritative state before use
- the patch only changes cleanup or logging with no acceptance or state-transition effect
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
