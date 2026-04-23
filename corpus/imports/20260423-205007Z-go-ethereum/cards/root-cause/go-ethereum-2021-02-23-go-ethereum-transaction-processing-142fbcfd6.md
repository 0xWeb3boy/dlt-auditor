# Root-Cause Card

## Metadata

- ID: `go-ethereum-2021-02-23-go-ethereum-transaction-processing-142fbcfd6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-replay-protection-enforcement`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `replay-protection`

## Violated Invariant

- Invariant: Transactions submitted through RPC should be replay-protected with EIP-155 by default unless an operator explicitly opts into accepting legacy unprotected transactions.

## Trust Boundary

- Boundary: Untrusted RPC or debug request parameters reaching privileged node logic.

## Attack Surface

- Entrypoint type: `rpc method`
- Sensitive sink: `expensive RPC-side computation, allocation, or response construction`

## Impact Pattern

- Primary impact: `replay-risk`
- Secondary impact: `transaction-integrity`

## Short Reusable Lesson

- The patch hardens go-ethereum RPC transaction submission by rejecting non-EIP-155, non-replay-protected transactions before SendTx unless rpc.allow-unprotected-txs is explicitly enabled.
