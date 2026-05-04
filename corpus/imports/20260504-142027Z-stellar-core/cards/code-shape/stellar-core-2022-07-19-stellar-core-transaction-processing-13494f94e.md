# Code-Shape Card

## Metadata

- ID: `stellar-core-2022-07-19-stellar-core-transaction-processing-13494f94e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-order-validation-hardening`

## Code Shape Summary

- A transaction-set container could be rebuilt by filtering and then reused without restoring hash order, while checkValid lacked an explicit is_sorted guard.

## Search Motifs

- filteredTxs assigned directly to mTxs
- TxSetFrame checkValid lacks is_sorted
- sortTxsInHashOrder after surge pricing
- hashTxSorter canonical order

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Validate canonical ordering with the same comparator used for protocol serialization and re-sort internal vectors after filtering.

## False Match Warnings

- If later serialization always sorts before consensus use, the issue is lower risk.
- Non-consensus mempool ordering may intentionally differ from canonical order.
- Duplicate checks are not equivalent to full ordering checks.
