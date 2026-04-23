# Root-Cause Card

## Metadata

- ID: `nitro-2022-06-01-nitro-transaction-processing-37c04d56b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `caller-controlled-withdrawal-destination`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fixed-withdrawal-destination`

## Violated Invariant

- Invariant: Privileged withdrawal operations should not accept an arbitrary caller-chosen destination when protocol or local policy expects a fixed authorized destination.

## Trust Boundary

- Boundary: `client or operator request->validator withdrawal path`

## Attack Surface

- Entrypoint type: `withdrawal-or-funds-movement`
- Sensitive sink: `constructing or submitting a withdrawal transaction`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Privileged withdrawal operations should not accept an arbitrary caller-chosen destination when protocol or local policy expects a fixed authorized destination. The grounded change is that the validator client no longer accepts or passes a configurable `withdrawDestination` when withdrawing staker funds. That is consistent with hardening a sensitive withdrawal path, but the provided excerpts do not establish a concrete vulnerability, exploit path, or the exact contract-side validation change. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
