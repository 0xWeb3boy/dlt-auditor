# Code-Shape Card

## Metadata

- ID: `rippled-2018-10-31-rippled-rpc-client-api-6bdc9e7b3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `wrong-revocation-cache`

## Code Shape Summary

- The grounded security fix is in ValidatorList::load: a configured validator-list publisher key was checked with validatorManifests_.revoked(id) before the patch and is checked with publisherManifests_.revoked(id) after the patch. Reusable shape: check for signer-scope-and-domain-binding was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: rpc-or-client-handler missing exact signer-scope-and-domain-binding check before node configuration, downloaded trust material, or externally visible service behavior
- Motif 2: security-sensitive path reaches node configuration, downloaded trust material, or externally visible service behavior before rejecting malformed, stale, or unauthorized input
- Motif 3: Use the revocation cache corresponding to the identity type being authorized.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into node configuration, downloaded trust material, or externally visible service behavior unless the signer-scope-and-domain-binding gate runs before the state-changing branch.

## Patch Pattern

- Use the revocation cache corresponding to the identity type being authorized.

## False Match Warnings

- No test contents are provided to show the exact regression scenario.
- No evidence shows live exploitation or production impact.
