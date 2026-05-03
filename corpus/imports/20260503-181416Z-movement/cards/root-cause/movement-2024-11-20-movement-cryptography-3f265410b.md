# Root-Cause Card

## Metadata

- ID: `movement-2024-11-20-movement-cryptography-3f265410b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signed-field-not-bound`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signed-message-field-binding`

## Violated Invariant

- Invariant: A signature over a structured protocol object must cover every field that affects object identity, routing, replay domain, or authorization decisions.

## Trust Boundary

- Boundary: Signed DA blob wrapper crossing from producer-controlled serialization into verifier-trusted blob identity.

## Attack Surface

- Entrypoint type: signed blob verification / DA ingestion
- Sensitive sink: acceptance of a verified blob identity for downstream DA processing

## Impact Pattern

- Primary impact: Signed metadata substitution or replay across wrapper identities.
- Secondary impact: Downstream DA state or routing confusion if id is trusted.

## Short Reusable Lesson

- The signature digest for a DA signed blob covered inner blob data and timestamp but not the wrapper id. The fix signs and verifies a digest that includes blob, timestamp, and id, binding the wrapper identity to the signature. Build the signed digest at the envelope layer and include all security-relevant wrapper fields before signature generation and verification.
