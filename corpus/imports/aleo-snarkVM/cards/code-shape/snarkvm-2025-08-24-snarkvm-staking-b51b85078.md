# Code-Shape Card

## Metadata

- ID: `snarkvm-2025-08-24-snarkvm-staking-b51b85078`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `deployment-upgrade-validation`

## Code Shape Summary

- Deployment upgrade validation checked constructor-related rules but did not visibly iterate existing functions to require presence and identical inputs under V10.

## Search Motifs

- upgrade verifier checks constructor but not all existing functions
- new program get_function(id) missing check
- function input interface equality gated by consensus version

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `upgrade-interface-preservation`.

## Patch Pattern

- For V10 and later, compare the new deployment against the stored program and reject missing existing functions or mismatched input types.

## False Match Warnings

- Another upgrade validation phase already checks function presence and full input/output equality.
- The consensus version is below the activation point for the new invariant.
- The changed functions are private or unreachable and not part of the stable interface.
