# Root-Cause Card

## Metadata

- ID: `geth-arb-2016-10-28-go-ethereum-transaction-processing-b59c8399fb`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signing-api-domain-separation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-domain-separation`

## Violated Invariant

- Invariant: Bytes signed through a general signing API must be domain-separated from transactions and protocol objects so a signature cannot be replayed as a different semantic object.

## Trust Boundary

- Boundary: wallet/RPC signing request -> account key material

## Attack Surface

- Entrypoint type: signing RPC or account API
- Sensitive sink: signature generation with reusable private key

## Impact Pattern

- Primary impact: signature-replay-prevention
- Secondary impact: account-safety
- Severity guide: low-medium

## Short Reusable Lesson

- The generic message-signing path needed an Ethereum-specific prefix and hash so arbitrary messages could not be confused with transactions or structured protocol payloads. Prefix and hash arbitrary messages under a dedicated domain before signing, and keep transaction signing on a distinct typed path.
