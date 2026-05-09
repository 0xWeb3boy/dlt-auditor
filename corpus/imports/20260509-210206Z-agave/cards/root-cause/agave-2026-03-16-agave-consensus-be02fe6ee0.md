# Root-Cause Card

## Metadata

- ID: `agave-2026-03-16-agave-consensus-be02fe6ee0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation-failure-masking`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `conjunctive-error-propagation`

## Violated Invariant

- Invariant: When two independent validation tasks guard the same consensus decision, success should require both to succeed and failure from either task must remain visible.

## Trust Boundary

- Boundary: `block-replay-and-verification-results->dead-slot-decision`

## Attack Surface

- Entrypoint type: `consensus-replay-completion`
- Sensitive sink: dead-slot marking and replay-stage failure handling
- Attacker capability: Deliver or influence blocks/slots that can make replay or verification fail independently.
- Key precondition: Independent replay and verification results are combined with disjunctive semantics.

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `fork-choice-integrity`
- Severity guidance: `medium` because Masking validation errors in replay-stage logic is consensus-sensitive, but no exploit, vote-safety bypass, or finalization impact was demonstrated.

## Short Reusable Lesson

- Replay-stage completion combines two independent Result values with an OR-like operation, allowing success from one branch to hide failure from the other.
- Structural fix: Replace disjunctive Result aggregation with conjunctive success semantics before consensus failure-handling decisions.
