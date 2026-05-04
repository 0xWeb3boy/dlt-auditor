# Validation Card

## Metadata

- ID: `stellar-core-2019-11-14-stellar-core-storage-57d10fae4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-archive-verification`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Command line gained extra verification support.
- Catchup work added DownloadVerifyTxResultsWork for the checkpoint range.
- The new work is inserted for OFFLINE_COMPLETE mode.

## What Could Have Invalidated It

- If tx result files are never consumed by the verifier or clients, impact is mostly audit completeness.
- If default online catchup never claims complete verification, the bug should be scoped to offline mode.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium_or_low
- Rationale: Archive verification gaps can affect trust in catchup data, but this finding is scoped to optional complete verification and does not prove live consensus impact.

## False-Positive Cautions

- Do not flag partial verification modes that are clearly documented as partial.
- Check whether omitted artifacts are consensus-critical or only diagnostic.
