# Code-Shape Card

## Metadata

- ID: `avalanchego-2023-09-27-avalanchego-transaction-processing-8e6f2f83e6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hardening-or-correctness-fix`

## Code Shape Summary

- Predicate checking gained explicit missing-context errors before verification-sensitive logic continues. The reusable shape is a validation function that accepts optional context but must require it whenever the checked object depends on it.

## Search Motifs

- nil PredicateContext checks added near predicate verification
- ErrMissingPredicateContext or fail-closed context errors
- early return only when no predicates are present

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Preserve early exits for objects that do not need context, but reject nil or incomplete context before verifying objects that do.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- No-predicate transactions may intentionally skip context
- A nil check in test scaffolding is not a vulnerability by itself
- Do not claim bypass unless required predicates can be evaluated without context
