# Root-Cause Card

## Metadata

- ID: `solana-2021-10-26-solana-staking-4fe3354c8f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-sysvar-account-input`
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

The issue was unsafe-by-default SDK ergonomics: a current-index helper accepted only raw bytes, so it could not enforce that the source was the authentic instructions sysvar. The evidence does not prove that an existing deployed program was exploitable.

## Impact Pattern

- Primary impact: input-validation, account-spoofing-resistance
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds safer Solana instructions-sysvar helper APIs and updates an example caller to use one of them. The evidence supports security-relevant hardening around sysvar identity checks and relative instruction lookup error handling, but not a confirmed vulnerability fix.
