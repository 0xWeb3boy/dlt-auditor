# Root-Cause Card

## Metadata

- ID: `solana-2020-11-24-solana-transaction-processing-db3f154b3f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `durable-nonce-failed-transaction-state-persistence`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `nonce-state-consistency`

## Violated Invariant

- Protocol input must satisfy nonce state consistency before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

The grounded root cause is an overly broad account persistence condition in the durable nonce failure path. The prior writable-account guard did not explicitly distinguish normal successful execution from failed durable-nonce execution, so the collection path could consider all writable accounts for storage instead of limiting the failure exception to nonce and fee-payer state.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The supported finding is a likely Solana runtime state-integrity fix in durable nonce transaction handling. The strongest evidence is the change in `Accounts::collect_accounts_to_store` from storing any writable account to storing writable accounts only on successful execution, or on failed durable-nonce execution when the account is the nonce account or fee payer. Related fee-calculator changes appear to support consistent durable-nonce metadata handli...
