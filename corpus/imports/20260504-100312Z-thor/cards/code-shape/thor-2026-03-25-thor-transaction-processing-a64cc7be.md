# Code-Shape Card

## Metadata

- ID: `thor-2026-03-25-thor-transaction-processing-a64cc7be`
- Bug family: `resource_accounting_and_limits`
- Bug class: `unbounded-rlp-list-decoding`

## Code Shape Summary

- Transaction RLP decoding accepted list-shaped reserved fields and clauses without explicit cardinality checks at the shown decode boundary; the fix pre-counts raw list entries and rejects values above protocol constants.

## Search Motifs

- rlp.Decode into []RawValue with no length check
- custom transaction list decoder missing max element guard
- decode list fully before comparing against Max*PerTx
- reserved or extension fields can repeat without bound

## Typical Asymmetry

- The external or cross-context input is treated as already safe, while the later privileged sink assumes that admission, domain, or cardinality checks already happened upstream.

## Patch Pattern

- Introduce bounded wrapper decoders, count raw list elements before object decoding, compare counts with protocol constants, and add regression tests for excessive list cardinality.

## False Match Warnings

- No issue if outer transaction size limits make the list count harmless.
- No issue if the decoder already streams and rejects after a small bounded count.
- Do not treat test helper additions alone as evidence without a production decode guard.
