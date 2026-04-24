# Validation Card

## Metadata

- ID: `geth-arb-2020-12-04-go-ethereum-transaction-processing-15339cf1c9`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `advisory-feed-authentication`

## What Confirmed The Issue

- Evidence 1: The phase-4 kept finding identifies a runtime change at `version/advisory feed fetcher` that changes acceptance, rejection, binding, bounds, or fail-closed behavior before `security warning, update recommendation, or operator trust decision`.
- Evidence 2: The patch pattern directly enforces `advisory-feed-authenticity` rather than only renaming code or improving diagnostics.

## What Could Have Invalidated It

- Compensating control 1: A mandatory upstream check proves the same invariant on every reachable path before this code runs.
- Compensating control 2: A downstream verifier recomputes the invariant fail-closed before any state, signature, network work, or privileged action is committed.

## Severity Guidance

- Expected impact band: security-hardening-or-defense-in-depth
- Expected severity band: low_or_informational
- Severity rationale: Confirmed fixes can justify the upper band; likely hardening cases should stay conservative unless call-path evidence proves attacker reachability and sink impact.

## False-Positive Cautions

- the signature covers chain ID, message type, domain, nonce, and freshness at the sink
- the object is never accepted from an untrusted boundary
- a later verifier rejects mismatched signer, domain, or sequence before side effects
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
