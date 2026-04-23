# Root-Cause Card

## Metadata

- ID: `reth-2023-08-03-reth-transaction-processing-3f63a0887`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `policy-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The evidence shows a real policy-data-flow fix in the transaction pool: the pending-listener notification path stopped accepting only a transaction hash and now receives the full `AddedTransaction`, from which it derives `propagate_allowed`. That supports a narrow conclusion that the old API dropped propagation-policy context before listener notification. However, the provided snippets do not show the full post-patch filtering logic or demonstrate that a network-facing listener actually leaked non-propagatable transactions, so the security thesis should be treated as unproven from this evidence alone.
