# Code-Shape Card

## Metadata

- ID: `firedancer-2025-03-21-firedancer-transaction-processing-f35407b68`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `memory-lifetime`

## Code Shape Summary

- The runtime stored CPI instruction metadata in a stack-local object even though later execution paths continued using it after the setup frame returned.

## Search Motifs

- Motif 1: stack-local metadata replaced with txn-owned array
- Motif 2: counter introduced for transaction-owned CPI info slots
- Motif 3: pointer to local struct escapes into later execution

## Typical Asymmetry

- Nested execution outlives the setup frame, but helper code treats stack-local metadata as if it had transaction lifetime.

## Patch Pattern

- Move escaped metadata into transaction-owned storage and make the ownership/lifetime explicit in setup and teardown code.

## False Match Warnings

- No concrete exploit path or attacker-controlled trigger is shown.
- No proof of consensus divergence, ledger corruption, or state-integrity violation is provided.
