# Root-Cause Card

## Metadata

- ID: `go-ethereum-2021-02-23-go-ethereum-transaction-processing-142fbcfd6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-replay-protection-enforcement`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch hardens go-ethereum RPC transaction submission by rejecting non-EIP-155, non-replay-protected transactions before SendTx unless rpc.allow-unprotected-txs is explicitly enabled.
