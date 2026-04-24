# Root-Cause Card

## Metadata

- ID: `sui-2022-01-25-sui-transaction-processing-f95e29b749`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-certificate-comparison-semantics`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: The input-validation property must be enforced before untrusted protocol data reaches a security-sensitive sink.

## Trust Boundary

- Boundary: submitted transaction or validator response -> execution/effects pipeline

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: committing security-sensitive protocol state

## Impact Pattern

- Primary impact: protocol-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch removes generic equality and hashing support from CertifiedOrder and from structs that embed it, because comparing or hashing certificates by their concrete signature sets can encode misleading certificate identity semantics.
