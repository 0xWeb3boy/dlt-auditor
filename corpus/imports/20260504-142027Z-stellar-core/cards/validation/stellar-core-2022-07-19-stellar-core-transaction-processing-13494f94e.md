# Validation Card

## Metadata

- ID: `stellar-core-2022-07-19-stellar-core-transaction-processing-13494f94e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-order-validation-hardening`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- TxSetFrame::checkValid gained an std::is_sorted check using hashTxSorter.
- surgePricingFilter now stores TxSetUtils::sortTxsInHashOrder(filteredTxs).

## What Could Have Invalidated It

- If the collection is private and sorted at every external boundary, internal unsortedness may be benign.
- If hash order is not consensus-relevant for the protocol version, severity should drop.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium_or_low
- Rationale: Canonical ordering affects deterministic processing, but evidence does not prove an exploit beyond ordering hardening and test failures.

## False-Positive Cautions

- Do not flag arbitrary container reordering unless a canonical order is specified.
- Verify comparator consistency across validation and serialization.
