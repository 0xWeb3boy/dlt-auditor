# Root-Cause Card

## Metadata

- ID: `oasis-core-2018-05-26-oasis-core-cryptography-19cd4a286`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signed-message-validation-consistency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signed-message-consistency`

## Violated Invariant

- Invariant: Signed requests should be verified once and then routed and executed using that same verified representation, and failures while extracting signed contents should abort processing.

## Trust Boundary

- Boundary: `peer->node`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `request-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Signed requests should be verified once and then routed and executed using that same verified representation, and failures while extracting signed contents should abort processing. In this pattern, the code previously did not consistently carry one verified signed representation through later processing. The patch indicates that signed payload handling relied on extracted or reconstructed values in some paths instead of preserving and reusing the verified wrapper end to end. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
