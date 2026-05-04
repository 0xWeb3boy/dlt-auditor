# Code-Shape Card

## Metadata

- ID: `stellar-core-2019-11-14-stellar-core-storage-57d10fae4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-archive-verification`

## Code Shape Summary

- The catchup work graph verified some history archive artifacts but did not include transaction result files until an explicit DownloadVerifyTxResultsWork step was added.

## Search Motifs

- OFFLINE_COMPLETE catchup missing tx results verification
- extra verification flag for archive files
- DownloadVerifyTxResultsWork added to catchup sequence
- history archive verifier only checks ledger headers and transactions

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Add a verifier work item for the omitted archive artifact type and wire it into the complete-verification catchup mode.

## False Match Warnings

- Optional audit modes may not protect live online catchup.
- If transaction results are independently hash-bound by checked ledgers, exploitability may be lower.
- Do not treat command-line option additions alone as security fixes.
