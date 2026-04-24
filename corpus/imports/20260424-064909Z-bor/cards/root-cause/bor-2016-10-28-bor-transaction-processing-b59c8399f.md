# Root-Cause Card

## Metadata

- ID: `bor-2016-10-28-bor-transaction-processing-b59c8399f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `message-signing-domain-separation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `signature authorization and domain binding`

## Violated Invariant

- Invariant: A signature or signer action must cover the full security context that gives the message authority, including domain, chain, signer scope, and payload semantics.

## Trust Boundary

- Boundary: external RPC/user signing request to local signer boundary

## Attack Surface

- Entrypoint type: RPC signing or transaction-submission method
- Sensitive sink: signature creation or signed transaction acceptance

## Impact Pattern

- Primary impact: unsafe-message-signing
- Secondary impact: high severity conditions

## Short Reusable Lesson

- The RPC/account signing boundary was too close to the low-level raw signing primitive, so user-supplied signing requests were not clearly forced into the Ethereum message-signing domain before signature generation.
