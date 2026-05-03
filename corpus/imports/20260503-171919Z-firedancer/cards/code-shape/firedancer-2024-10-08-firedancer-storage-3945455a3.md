# Code-Shape Card

## Metadata

- ID: `firedancer-2024-10-08-firedancer-storage-3945455a3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `runtime-program-admissibility`

## Code Shape Summary

- The execution path lacked a dedicated admissibility gate and trusted downstream logic to notice invalid program accounts too late.

## Search Motifs

- Motif 1: pre-execution executable-program check added
- Motif 2: transaction aborted before dispatch on invalid program account
- Motif 3: runtime admissibility helper inserted ahead of interpreter entry

## Typical Asymmetry

- Transaction metadata selects the program account, but the executor assumes that account has already passed all admissibility checks.

## Patch Pattern

- Add a pre-dispatch admissibility helper and fail the transaction before any execution state is initialized.

## False Match Warnings

- Exact blacklist entries and matching logic are not shown.
- No end-to-end attacker-controlled exploit path is shown.
