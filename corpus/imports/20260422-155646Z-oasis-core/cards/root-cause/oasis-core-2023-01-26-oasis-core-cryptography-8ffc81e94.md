# Root-Cause Card

## Metadata

- ID: `oasis-core-2023-01-26-oasis-core-cryptography-8ffc81e94`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `insufficient-peer-identity-verification`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `peer-identity-binding`

## Violated Invariant

- Invariant: For explicit key manager member calls over Noise, the enclave must learn which node was selected and bind the authenticated session to that intended member using trusted identity material from consensus.

## Trust Boundary

- Boundary: `host->enclave`

## Attack Surface

- Entrypoint type: `session-setup`
- Sensitive sink: `secure session cache`

## Impact Pattern

- Primary impact: `identity-misbinding`
- Secondary impact: `none`

## Short Reusable Lesson

- For explicit key manager member calls over Noise, the enclave must learn which node was selected and bind the authenticated session to that intended member using trusted identity material from consensus. In this pattern, explicit-member routing needed additional identity-binding state across the host/session boundary. The provided evidence shows that this state was previously not exposed in the relevant APIs, so explicit peer selection could not be tied as directly to session identity verification as it is after the patch. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
