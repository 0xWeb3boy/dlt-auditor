# Root-Cause Card

## Metadata

- ID: `movement-2025-01-15-movement-rpc-client-api-c008e2912`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-verification`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `known-signer-verification-before-response`

## Violated Invariant

- Invariant: Data returned across a trusted light-node or RPC read boundary must be verified against the configured signer set before it is serialized as trusted output.

## Trust Boundary

- Boundary: DA stream data crossing from an external availability source into light-node RPC responses consumed by clients.

## Attack Surface

- Entrypoint type: streaming read API / pass-through RPC response generation
- Sensitive sink: serialization of DA blob contents as verified pass-through output

## Impact Pattern

- Primary impact: Unverified external DA data exposed as trusted RPC output.
- Secondary impact: Client state contamination or acceptance of data outside the configured signer set.

## Short Reusable Lesson

- A DA light-node pass-through read stream serialized each DA blob directly into an RPC response. The fix wires a VerifierOperations implementation into the light-node type and calls verifier.verify(blob, height) before serializing only the verified inner blob. Thread a verifier dependency into the stream service, verify each blob at its DA height before response construction, and change response serialization to consume verified inner data only.
