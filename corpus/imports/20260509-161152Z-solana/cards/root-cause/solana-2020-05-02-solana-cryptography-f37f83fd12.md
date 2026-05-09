# Root-Cause Card

## Metadata

- ID: `solana-2020-05-02-solana-cryptography-f37f83fd12`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sanitization-ordering`
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

The provided evidence supports only that validation was split across stages and was moved earlier into the account-locking path. It does not show that this ordering allowed an attacker to bypass locks, corrupt state, forge signatures, replay transactions, or otherwise exploit the runtime.

## Impact Pattern

- Primary impact: malformed-transaction-rejection, runtime-validation-hardening
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch moves transaction sanitization and duplicate account-key rejection into `Accounts::lock_accounts`, before account lock key extraction. It removes the duplicate-key check from `load_tx_accounts` and removes the shown later `Bank::check_refs` sanitization path. This is a grounded validation-order cleanup or hardening change, but the supplied evidence does not prove a vulnerability, exploitability, consensus break, balance impact, replay issue, o...
