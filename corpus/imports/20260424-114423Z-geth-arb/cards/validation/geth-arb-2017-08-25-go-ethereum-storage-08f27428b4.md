# Validation Card

## Metadata

- ID: `geth-arb-2017-08-25-go-ethereum-storage-08f27428b4`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `contract-address-collision-prevention`

## What Confirmed The Issue

- Evidence 1: The phase-4 kept finding identifies a runtime change at `EVM CREATE/contract deployment path` that changes acceptance, rejection, binding, bounds, or fail-closed behavior before `new contract account creation and code installation`.
- Evidence 2: The patch pattern directly enforces `account-creation-collision-check` rather than only renaming code or improving diagnostics.

## What Could Have Invalidated It

- Compensating control 1: A mandatory upstream check proves the same invariant on every reachable path before this code runs.
- Compensating control 2: A downstream verifier recomputes the invariant fail-closed before any state, signature, network work, or privileged action is committed.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low
- Severity rationale: Confirmed fixes can justify the upper band; likely hardening cases should stay conservative unless call-path evidence proves attacker reachability and sink impact.

## False-Positive Cautions

- state is invalidated on every relevant reorg, fork, mode, or configuration change
- the sink re-reads authoritative state before use
- the patch only changes cleanup or logging with no acceptance or state-transition effect
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
