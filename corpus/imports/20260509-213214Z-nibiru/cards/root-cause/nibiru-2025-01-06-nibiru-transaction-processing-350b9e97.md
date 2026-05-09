# Root-Cause Card

## Metadata

- ID: `nibiru-2025-01-06-nibiru-transaction-processing-350b9e97`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-undercharge`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `accurate gas measurement for wrapped operations`

## Violated Invariant

- Invariant: A wrapper that charges gas for delegated state operations must measure the real operation cost, not a discounted or zero-cost substitute context.

## Trust Boundary

- Boundary: Protocol wrapper crosses from a high-level bank operation into low-level KV/transient store gas accounting.

## Attack Surface

- Entrypoint type: bank operation wrapped by a forced gas invariant helper
- Sensitive sink: transaction gas meter charge for storage-heavy bank side effects

## Impact Pattern

- Primary impact: gas undercharge
- Secondary impact: resource exhaustion risk from underpriced storage work

## Short Reusable Lesson

- A gas invariant wrapper measured bank operations under zero-cost store gas settings and then charged the real transaction meter from that discounted measurement.
