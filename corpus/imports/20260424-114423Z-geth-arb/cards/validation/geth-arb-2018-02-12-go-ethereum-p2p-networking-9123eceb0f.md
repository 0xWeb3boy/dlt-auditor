# Validation Card

## Metadata

- ID: `geth-arb-2018-02-12-go-ethereum-p2p-networking-9123eceb0f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reply-correlation-hardening`

## What Confirmed The Issue

- Evidence 1: The phase-4 kept finding identifies a runtime change at `p2p ping/pong handler` that changes acceptance, rejection, binding, bounds, or fail-closed behavior before `node bonding, liveness confirmation, or request completion`.
- Evidence 2: The patch pattern directly enforces `request-reply-correlation` rather than only renaming code or improving diagnostics.

## What Could Have Invalidated It

- Compensating control 1: A mandatory upstream check proves the same invariant on every reachable path before this code runs.
- Compensating control 2: A downstream verifier recomputes the invariant fail-closed before any state, signature, network work, or privileged action is committed.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: low_or_informational
- Severity rationale: Confirmed fixes can justify the upper band; likely hardening cases should stay conservative unless call-path evidence proves attacker reachability and sink impact.

## False-Positive Cautions

- an earlier mandatory check rejects the same malformed field on every reachable path
- the changed code is test-only, logging-only, generated-only, or pure refactor
- a downstream consensus or proof verifier recomputes the property fail-closed before state changes are committed
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
