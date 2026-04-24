# Root-Cause Card

## Metadata

- ID: `bor-2020-05-17-bor-rpc-client-api-868dc81c8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fail-open-error-handling`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus invariant enforcement`

## Violated Invariant

- Invariant: RPC-facing code must fail closed and enforce request limits and authorization before exposing backend state or privileged behavior.

## Trust Boundary

- Boundary: external RPC client to node service boundary

## Attack Surface

- Entrypoint type: public or administrative RPC method
- Sensitive sink: backend state access, privileged API behavior, or response serialization

## Impact Pattern

- Primary impact: state-consistency
- Secondary impact: low severity conditions

## Short Reusable Lesson

- The only clearly supported issue is permissive error handling in a consensus-related path: FinalizeAndAssemble could continue after CommitStates failed. The rest of the diff shows restructuring around canonical contract-backed helpers, but the evidence does not prove the old local logic was unsafe rather than simply being replaced.
