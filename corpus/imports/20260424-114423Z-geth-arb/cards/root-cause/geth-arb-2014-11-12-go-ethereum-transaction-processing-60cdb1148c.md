# Root-Cause Card

## Metadata

- ID: `geth-arb-2014-11-12-go-ethereum-transaction-processing-60cdb1148c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-commitment-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `block-body-commitment-integrity`

## Violated Invariant

- Invariant: A block body must be checked against the commitment or transaction root carried by its header before the node accepts, executes, or propagates that block.

## Trust Boundary

- Boundary: untrusted block payload -> local block import and execution

## Attack Surface

- Entrypoint type: block import or peer block-processing path
- Sensitive sink: block acceptance, transaction execution, and canonical state update

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: state-integrity
- Severity guide: high

## Short Reusable Lesson

- Block-processing code had the transaction commitment comparison present but disabled, allowing body data to approach execution without proving it matched the header commitment. Restore the body-root recomputation and equality check at block import, and fail closed before execution when the header commitment does not match.
