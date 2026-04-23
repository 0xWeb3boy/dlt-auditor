# Root-Cause Card

## Metadata

- ID: `go-ethereum-2016-10-28-go-ethereum-transaction-processing-b59c8399f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-separation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `domain-separated-signing`

## Violated Invariant

- Invariant: Account-signing RPC methods should not expose raw ECDSA signing over caller-controlled input in a form that can be confused with other Ethereum signature contexts; arbitrary messages should be domain-prefixed and hashed before signing.

## Trust Boundary

- Boundary: Untrusted RPC or debug request parameters reaching privileged node logic.

## Attack Surface

- Entrypoint type: `rpc method`
- Sensitive sink: `expensive RPC-side computation, allocation, or response construction`

## Impact Pattern

- Primary impact: `signature-misuse-risk`
- Secondary impact: `private-key-exposure-risk`

## Short Reusable Lesson

- The patch is best classified as security hardening for go-ethereum RPC/account signing.
