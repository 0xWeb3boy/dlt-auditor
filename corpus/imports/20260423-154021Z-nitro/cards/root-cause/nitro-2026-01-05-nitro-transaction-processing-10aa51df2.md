# Root-Cause Card

## Metadata

- ID: `nitro-2026-01-05-nitro-transaction-processing-10aa51df2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-validation-recording`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `mandatory-validation-witness-recording`

## Violated Invariant

- Invariant: When later validation depends on auxiliary witnesses such as tx-indexed logs, recording those witnesses should be mandatory and failure should abort the extraction path.

## Trust Boundary

- Boundary: `parent-chain log consumption->MEL extraction witness recording`

## Attack Surface

- Entrypoint type: `extraction-or-witness-recording`
- Sensitive sink: `continuing extraction without the witness data later validation needs`

## Impact Pattern

- Primary impact: `validation-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- When later validation depends on auxiliary witnesses such as tx-indexed logs, recording those witnesses should be mandatory and failure should abort the extraction path. The grounded change is that MEL extraction now records tx-indexed logs when consuming certain parent-chain logs, and aborts if that recording fails. That supports later MEL validation, but the provided evidence does not establish a concrete vulnerability, exploit path, or prior security bypass. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
