# Code-Shape Card

## Metadata

- ID: `stellar-core-2015-06-01-stellar-core-cryptography-a0bd68890`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vblocking-threshold-off-by-one`

## Code Shape Summary

- A recursive consensus blocking predicate initialized its remaining-count threshold one too low, misclassifying edge cases around quorum-set blocking.

## Search Motifs

- isVBlocking computes validators plus innerSets minus threshold
- N - T without plus one
- off-by-one quorum threshold tests
- vblocking and quorum test added

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Correct the threshold formula in the consensus predicate and add focused tests for quorum and v-blocking edge cases.

## False Match Warnings

- Different consensus protocols may define blocking as N - T, so compare against the local spec.
- Test expectation changes alone are not enough without predicate arithmetic changes.
- Misclassification only in diagnostics is lower risk than in live consensus.
