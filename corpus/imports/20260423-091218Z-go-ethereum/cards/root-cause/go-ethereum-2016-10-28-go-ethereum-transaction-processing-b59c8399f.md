# Root-Cause Card

## Metadata

- ID: `go-ethereum-2016-10-28-go-ethereum-transaction-processing-b59c8399f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-separation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `message-domain separation`

## Violated Invariant

- Invariant: Externally reachable signing APIs should only produce signatures in a clearly scoped message domain so caller-controlled input cannot be repurposed across signing contexts.

## Trust Boundary

- Boundary: RPC or wallet-facing signing requests -> private-key operations inside the node.

## Attack Surface

- Entrypoint type: Account-signing RPC request.
- Sensitive sink: Producing an ECDSA signature with a managed account key.

## Impact Pattern

- Primary impact: Signature misuse through ambiguous signing scope.
- Secondary impact: Increased exposure to chosen-input signing risks at the wallet boundary.

## Short Reusable Lesson

- A signing primitive can be safe internally and still be unsafe as an external API. Message-signing endpoints need explicit domain separation so callers cannot obtain signatures that are valid outside the intended user-message context.
