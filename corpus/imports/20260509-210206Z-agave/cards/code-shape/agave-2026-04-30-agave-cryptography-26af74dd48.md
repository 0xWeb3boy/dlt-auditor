# Code-Shape Card

## Metadata

- ID: `agave-2026-04-30-agave-cryptography-26af74dd48`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-protocol-validation`

## Code Shape Summary

- The ledger recovery path constructs or inserts recovered shreds through a separate code path that may not apply the current protocol rule for unexpected data-complete flags.

## Search Motifs

- recovered shreds bypass direct validation rule
- data_complete flag not checked after Reed Solomon recovery
- ShredRecoveryContext missing from blockstore insertion
- feature gated shred validation absent in recovery path

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Route recovered shreds through protocol-aware recovery context and add regression coverage that feature-gated invalid recovered data shreds are discarded.

## False Match Warnings

- Recovered shreds are re-run through the exact same validator as received shreds before use.
- The unexpected flag cannot be attacker-influenced or cannot survive recovery.
- The change only adds test coverage without altering recovery handling.
