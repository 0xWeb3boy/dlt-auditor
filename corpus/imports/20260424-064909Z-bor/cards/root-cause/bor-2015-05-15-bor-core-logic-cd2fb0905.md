# Root-Cause Card

## Metadata

- ID: `bor-2015-05-15-bor-core-logic-cd2fb0905`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource limit and input validity enforcement`

## Violated Invariant

- Invariant: Attacker-controlled input must be bounded and rejected before it can drive unbounded allocation, expensive processing, queue growth, or process termination.

## Trust Boundary

- Boundary: untrusted block, header, transaction, or state data to consensus engine boundary

## Attack Surface

- Entrypoint type: block/header/transaction validation or state-transition path
- Sensitive sink: canonical chain selection, state root commitment, or consensus state mutation

## Impact Pattern

- Primary impact: remote-dos
- Secondary impact: high severity conditions

## Short Reusable Lesson

- The downloader accepted non-terminal hash responses without validating that they advanced local queue state. Because the queue insertion API did not report whether anything new was added, the caller could stay in a request/response loop with a peer that kept sending duplicate hashes.
