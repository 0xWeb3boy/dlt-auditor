# Validation Card

## Metadata

- ID: `geth-arb-2022-01-26-go-ethereum-transaction-processing-b5048b881e`
- Bug family: `authz_and_role_gates`
- Bug class: `sequencer-fee-policy-bypass`

## What Confirmed The Issue

- Evidence 1: The phase-4 kept finding identifies a runtime change at `sequencer transaction admission filter` that changes acceptance, rejection, binding, bounds, or fail-closed behavior before `sequencer ordering and fee-routing decision`.
- Evidence 2: The patch pattern directly enforces `sequencer-admission-policy` rather than only renaming code or improving diagnostics.

## What Could Have Invalidated It

- Compensating control 1: A mandatory upstream check proves the same invariant on every reachable path before this code runs.
- Compensating control 2: A downstream verifier recomputes the invariant fail-closed before any state, signature, network work, or privileged action is committed.

## Severity Guidance

- Expected impact band: economic-or-funds-safety
- Expected severity band: medium_or_low
- Severity rationale: Confirmed fixes can justify the upper band; likely hardening cases should stay conservative unless call-path evidence proves attacker reachability and sink impact.

## False-Positive Cautions

- a separate mandatory role check guards the sink
- errors fail closed before privilege is granted
- the changed path only affects local diagnostics and not authorization or privilege
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
