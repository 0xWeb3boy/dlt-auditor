# Root-Cause Card

## Metadata

- ID: `bor-2021-02-23-bor-transaction-processing-142fbcfd6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-replay-protection-check`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `replay-protection and signature domain binding`

## Violated Invariant

- Invariant: Signed messages and transactions must be bound to the intended chain, domain, nonce, and execution context before they are accepted or relayed.

## Trust Boundary

- Boundary: external RPC/user signing request to local signer boundary

## Attack Surface

- Entrypoint type: RPC signing or transaction-submission method
- Sensitive sink: signature creation or signed transaction acceptance

## Impact Pattern

- Primary impact: transaction-replay
- Secondary impact: high severity conditions

## Short Reusable Lesson

- The RPC submission boundary did not enforce replay protection by default. In the provided pre-patch snippet, unprotected transactions could pass the visible fee-cap checks and reach SendTx without a shown EIP-155 protection check.
