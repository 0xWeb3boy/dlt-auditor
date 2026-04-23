# Code-Shape Card

## Metadata

- ID: `reth-2023-08-03-reth-transaction-processing-3f63a0887`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `policy-enforcement`

## Code Shape Summary

- The evidence shows a real policy-data-flow fix in the transaction pool: the pending-listener notification path stopped accepting only a transaction hash and now receives the full `AddedTransaction`, from which it derives `propagate_allowed`. That supports a narrow conclusion that the old API dropped propagation-policy context before listener notification. However, the provided snippets do not show the full post-patch filtering logic or demonstrate that a network-facing listener actually leaked non-propagatable transactions, so the security thesis should be treated as unproven from this evidence alone.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
