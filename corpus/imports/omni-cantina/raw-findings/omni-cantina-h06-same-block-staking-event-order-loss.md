# Raw Finding Summary

Source: Omni Cantina `H-6`
Title: Validator deposit will be lost if delegation happens in the same block as validator creation
Severity: `high`

## Normalized Summary

The report shows CreateValidator and Delegate events from the same block being sorted by event topic. Delegate sorts before CreateValidator, so native delivery sees no validator and loses the delegation.

## Reusable Failure Shape

Source logs are sorted lexicographically by reduced fields rather than source log index, so Delegate can be delivered before same-block CreateValidator.

## Missing Property

`source-event-order-preservation`: Cross-runtime generated events that encode dependent state transitions must preserve source log order or fail/retry atomically when a dependency is not ready.

## Source Evidence

- Ground-truth findings file: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Source section: `H-6`
