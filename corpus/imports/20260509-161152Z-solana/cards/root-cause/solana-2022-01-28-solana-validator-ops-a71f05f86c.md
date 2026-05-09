# Root-Cause Card

## Metadata

- ID: `solana-2022-01-28-solana-validator-ops-a71f05f86c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cpi-duplicate-account-privilege-escalation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization-and-privilege-check`

## Violated Invariant

- Protocol input must satisfy authorization and privilege check before it can reach stake delegation, withdrawal, reward accounting, vote authority, or validator weight.

## Trust Boundary

- Boundary: signed stake/vote instruction to stake-weighted accounting state

## Attack Surface

- Entrypoint type: stake or vote program instruction
- Sensitive sink: stake delegation, withdrawal, reward accounting, vote authority, or validator weight

## Root Cause

Privilege validation occurred too early relative to duplicate account normalization. Because duplicate metas can update an existing deduplicated `InstructionAccount` by ORing privilege bits such as `is_writable`, the final effective privileges could differ from the state that had already been checked.

## Impact Pattern

- Primary impact: privilege-escalation, authorization-bypass
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch fixes CPI duplicate account privilege handling in Solana's instruction preparation path. Duplicate account metas are normalized by merging privilege bits, so privilege checks must be applied after deduplication to the final effective account entry. The supplied implementation evidence directly shows writable privilege validation moved from inside the deduplication loop to a post-deduplication pass; signer coverage is supported by the commit me...
