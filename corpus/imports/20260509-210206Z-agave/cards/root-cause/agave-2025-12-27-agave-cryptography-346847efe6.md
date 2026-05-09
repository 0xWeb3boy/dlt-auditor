# Root-Cause Card

## Metadata

- ID: `agave-2025-12-27-agave-cryptography-346847efe6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-state-validation-timing`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fresh-state-revalidation`

## Violated Invariant

- Invariant: Mutable replay-protection state and its authority must be reloaded and validated at the execution boundary, not only at an earlier preflight or age-check boundary.

## Trust Boundary

- Boundary: `signed-transaction->svm-execution`

## Attack Surface

- Entrypoint type: `transaction-state-transition`
- Sensitive sink: durable nonce execution state acceptance
- Attacker capability: Submit durable-nonce transactions whose nonce account state may change between early checking and execution.
- Key precondition: Nonce account locks or execution ordering allow account state to differ after an early check.

## Impact Pattern

- Primary impact: `replay-protection`
- Secondary impact: `state-integrity`
- Severity guidance: `medium` because Fresh nonce validation protects replay-sensitive transaction state, but the evidence did not prove unauthorized acceptance, fund loss, or a concrete exploit.

## Short Reusable Lesson

- Nonce authority and account state are validated early in bank transaction-age handling, then reused later even though the nonce account is mutable before SVM processing.
- Structural fix: Defer nonce execution-state construction to SVM processing and reload/revalidate the current nonce account and authority immediately before processing.
