# Root-Cause Card

## Metadata

- ID: `solana-2020-05-02-solana-transaction-processing-fa254ff18f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-transaction-validation-ordering`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-shape-validation`

## Violated Invariant

- Protocol input must satisfy input shape validation before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

The grounded root cause is validation ordering and duplication: malformed transaction checks were split across account locking, post-lock bank validation, and account loading. The evidence does not show a concrete state corruption, unauthorized access, balance impact, consensus failure, or remotely exploitable crash.

## Impact Pattern

- Primary impact: transaction-validation-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch moves transaction sanitization and duplicate-account-key rejection into `Accounts::lock_accounts` before lock key derivation, removes the duplicate-key rejection from later account loading, and removes a separate post-lock reference-check path in `Bank`. This is plausibly security relevant because it affects malformed transaction handling in runtime account locking, but the evidence does not prove a vulnerability or exploit path.
