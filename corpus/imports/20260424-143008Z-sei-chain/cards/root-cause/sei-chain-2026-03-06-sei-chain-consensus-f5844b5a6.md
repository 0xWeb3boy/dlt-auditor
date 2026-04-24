# Root-Cause Card

## Metadata

- ID: `sei-chain-2026-03-06-sei-chain-consensus-f5844b5a6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-lock-preservation`

## Violated Invariant

- Invariant: Timeout-driven view changes must preserve the latest consensus lock/certificate so later votes and proposals remain constrained by safety rules.

## Trust Boundary

- Boundary: timeout certificate from prior view -> timeout vote construction in new view

## Attack Surface

- Entrypoint type: consensus-timeout-vote-handler
- Sensitive sink: emitting TimeoutVotes/TimeoutQCs that influence later proposal eligibility

## Impact Pattern

- Primary impact: consensus-failure
- Secondary impact: consensus-integrity-or-liveness

## Short Reusable Lesson

- Preserve consensus lock state at the vote-construction boundary by falling back from current-view state to the lock already carried in the justifying certificate. Protects a consensus safety invariant rather than confidentiality or authentication. Prevents PrepareQC lock loss across consecutive timeout-driven views.
