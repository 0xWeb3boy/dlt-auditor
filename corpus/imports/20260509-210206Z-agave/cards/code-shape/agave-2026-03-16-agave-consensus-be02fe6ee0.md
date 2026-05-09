# Code-Shape Card

## Metadata

- ID: `agave-2026-03-16-agave-consensus-be02fe6ee0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation-failure-masking`

## Code Shape Summary

- Replay-stage completion combines two independent Result values with an OR-like operation, allowing success from one branch to hide failure from the other.

## Search Motifs

- Result::or used to combine validation results
- replay result and verify result require both success
- dead slot marking skipped when one async task succeeds
- validation error masking in consensus pipeline

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Replace disjunctive Result aggregation with conjunctive success semantics before consensus failure-handling decisions.

## False Match Warnings

- The OR combines alternative equivalent checks where either success is intentionally sufficient.
- Masked errors are used only for logging and cannot affect consensus decisions.
- A separate mandatory check marks the slot dead on either failure.
