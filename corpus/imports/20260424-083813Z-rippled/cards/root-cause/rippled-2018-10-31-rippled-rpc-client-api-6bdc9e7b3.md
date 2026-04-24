# Root-Cause Card

## Metadata

- ID: `rippled-2018-10-31-rippled-rpc-client-api-6bdc9e7b3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `wrong-revocation-cache`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `signer-scope-and-domain-binding`

## Violated Invariant

- Invariant: Signed or hashed protocol objects must bind the intended signer, object type, domain, and revocation state before the object is trusted.

## Trust Boundary

- Boundary: remote client or configured service endpoint -> local RPC/client trust boundary

## Attack Surface

- Entrypoint type: rpc-or-client-handler
- Sensitive sink: node configuration, downloaded trust material, or externally visible service behavior

## Impact Pattern

- Primary impact: revocation-bypass, trust-validation-bypass
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The grounded security fix is in ValidatorList::load: a configured validator-list publisher key was checked with validatorManifests_.revoked(id) before the patch and is checked with publisherManifests_.revoked(id) after the patch.
