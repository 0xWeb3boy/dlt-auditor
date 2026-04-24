# Code-Shape Card

## Metadata

- ID: `rippled-2024-04-22-rippled-core-logic-3f7ce939c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `amm-rounding-invariant-hardening`

## Code Shape Summary

- The provided evidence supports a likely security-relevant AMM accounting fix. The commit states that swap rounding could sometimes violate the AMM balance-product invariant by very small amounts and introduces the fixAMMRounding amendment so rounding favors the AMM. Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact accounting-integrity check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Use a consensus amendment to change AMM rounding semantics so arithmetic preserves the protocol accounting invariant, with adjacent runtime and compile-time guards around amount handling.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Use a consensus amendment to change AMM rounding semantics so arithmetic preserves the protocol accounting invariant, with adjacent runtime and compile-time guards around amount handling.

## False Match Warnings

- The supplied hunks do not show the actual AMM rounding arithmetic change.
- No transaction-level exploit, proof of profit, or drain scenario is provided.
