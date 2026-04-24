# Validation Card

## Metadata

- ID: `geth-arb-2025-04-08-go-ethereum-transaction-processing-2e739fce58`
- Bug family: `resource_accounting_and_limits`
- Bug class: `txpool-resource-exhaustion-hardening`

## What Confirmed The Issue

- Evidence 1: The phase-4 kept finding identifies a runtime change at `transaction pool validation path` that changes acceptance, rejection, binding, bounds, or fail-closed behavior before `mempool resource reservation and peer propagation`.
- Evidence 2: The patch pattern directly enforces `txpool-resource-isolation` rather than only renaming code or improving diagnostics.

## What Could Have Invalidated It

- Compensating control 1: A mandatory upstream check proves the same invariant on every reachable path before this code runs.
- Compensating control 2: A downstream verifier recomputes the invariant fail-closed before any state, signature, network work, or privileged action is committed.

## Severity Guidance

- Expected impact band: availability-or-resource-exhaustion
- Expected severity band: medium_or_high
- Severity rationale: Confirmed fixes can justify the upper band; likely hardening cases should stay conservative unless call-path evidence proves attacker reachability and sink impact.

## False-Positive Cautions

- a hard request cap is enforced before allocation or network work
- peer scoring or authentication makes repeated abuse impractical
- the path is operator-only and unreachable from untrusted clients
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
