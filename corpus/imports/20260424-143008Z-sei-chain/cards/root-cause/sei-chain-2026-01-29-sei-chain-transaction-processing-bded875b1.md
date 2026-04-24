# Root-Cause Card

## Metadata

- ID: `sei-chain-2026-01-29-sei-chain-transaction-processing-bded875b1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mock-balance-mainnet-guard`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `production-safety-guard`

## Violated Invariant

- Invariant: Testing-only state mutation helpers must be unreachable or fail closed on production networks, especially from read paths.

## Trust Boundary

- Boundary: build-tag or mock balance helper -> production ledger state

## Attack Surface

- Entrypoint type: mock-balance-read-or-mutation-helper
- Sensitive sink: minting, top-off, or mutating balances

## Impact Pattern

- Primary impact: misconfiguration-containment
- Secondary impact: state-accounting

## Short Reusable Lesson

- Move testing-only mock balance funding out of observational read paths into explicit preparation or mutation paths, and place direct mainnet safety guards on those paths. Mock balance code can add funds, so accidental mainnet execution would be high impact. Direct pacific-1 guards reduce the risk from a bad mock_balances build or deployment configuration.
