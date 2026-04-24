# Validation Card

## Metadata

- ID: `geth-arb-2018-09-25-go-ethereum-cryptography-d3441ebb56`
- Bug family: `authz_and_role_gates`
- Bug class: `signer-boundary-policy-hardening`

## What Confirmed The Issue

- Evidence 1: The phase-4 kept finding identifies a runtime change at `signer transaction validation path` that changes acceptance, rejection, binding, bounds, or fail-closed behavior before `user-mediated or policy-mediated signature generation`.
- Evidence 2: The patch pattern directly enforces `signing-policy-fail-closed` rather than only renaming code or improving diagnostics.

## What Could Have Invalidated It

- Compensating control 1: A mandatory upstream check proves the same invariant on every reachable path before this code runs.
- Compensating control 2: A downstream verifier recomputes the invariant fail-closed before any state, signature, network work, or privileged action is committed.

## Severity Guidance

- Expected impact band: authorization-or-signature-integrity
- Expected severity band: low_or_informational
- Severity rationale: Confirmed fixes can justify the upper band; likely hardening cases should stay conservative unless call-path evidence proves attacker reachability and sink impact.

## False-Positive Cautions

- a separate mandatory role check guards the sink
- errors fail closed before privilege is granted
- the changed path only affects local diagnostics and not authorization or privilege
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
