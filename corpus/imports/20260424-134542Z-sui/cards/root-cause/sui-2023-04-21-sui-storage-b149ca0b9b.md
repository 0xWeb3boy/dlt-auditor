# Root-Cause Card

## Metadata

- ID: `sui-2023-04-21-sui-storage-b149ca0b9b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `wallet-content-script-message-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Malformed or adversarial inputs must be rejected before they reach parsing, execution, or state-commit logic that assumes well-formed data.

## Trust Boundary

- Boundary: executed effects or checkpoint data -> authenticated persistent state

## Attack Surface

- Entrypoint type: state-transition-storage-update
- Sensitive sink: persisting or serving authenticated ledger state

## Impact Pattern

- Primary impact: unauthorized-wallet-data-access-prevention
- Secondary impact: message-boundary-hardening

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. Wallet-ext: test site-cs messaging (#9444) looks like a focused hardening change in the storage path of sui. The strongest evidence spans `apps/wallet/src/background/connections/ContentScriptConnection.ts` and `apps/wallet/playwright.config.ts`. The affected state likely includes `command`, `port`, and `process`.
