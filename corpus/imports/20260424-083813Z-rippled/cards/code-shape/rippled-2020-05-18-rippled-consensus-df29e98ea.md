# Code-Shape Card

## Metadata

- ID: `rippled-2020-05-18-rippled-consensus-df29e98ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-threshold-rounding`

## Code Shape Summary

- The provided evidence supports a consensus-amendment threshold rounding fix. The commit message explicitly says amendment ballot counting could allow majority with slightly less than 80% support due to integer arithmetic and rounding semantics. Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: consensus-message-or-ledger-close-path missing exact accounting-integrity check before ledger close decision, validator set decision, or consensus safety state
- Motif 2: security-sensitive path reaches ledger close decision, validator set decision, or consensus safety state before rejecting malformed, stale, or unauthorized input
- Motif 3: Make the consensus activation threshold explicit and computed from the trusted validation set and consensus rules, avoiding reliance on an integer-scaled ratio that can obscure or lower the intended threshold.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger close decision, validator set decision, or consensus safety state unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Make the consensus activation threshold explicit and computed from the trusted validation set and consensus rules, avoiding reliance on an integer-scaled ratio that can obscure or lower the intended threshold.

## False Match Warnings

- No evidence that an amendment actually activated incorrectly.
- No evidence of a realized fork or consensus split from the rounding flaw.
