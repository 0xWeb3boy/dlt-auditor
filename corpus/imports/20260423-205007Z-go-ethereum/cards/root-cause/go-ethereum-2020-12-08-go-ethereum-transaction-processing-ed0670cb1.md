# Root-Cause Card

## Metadata

- ID: `go-ethereum-2020-12-08-go-ethereum-transaction-processing-ed0670cb1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `replay-protection`

## Violated Invariant

- Invariant: Contract transaction signing should use a signer appropriate to the target chain. On EIP-155 chains, callers should be able to bind signatures to the intended chainID rather than always producing legacy Homestead-style signatures.

## Trust Boundary

- Boundary: Untrusted RPC or debug request parameters reaching privileged node logic.

## Attack Surface

- Entrypoint type: `rpc method`
- Sensitive sink: `expensive RPC-side computation, allocation, or response construction`

## Impact Pattern

- Primary impact: `cross-chain-replay-risk`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The evidence supports replay-protection hardening in go-ethereum contract binding transaction option creation.
