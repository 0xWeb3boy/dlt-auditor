# Code-Shape Card

## Metadata

- ID: `oasis-core-2021-02-15-oasis-core-cryptography-a0ac508da`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `insufficient-signature-domain-separation`

## Code Shape Summary

- Short description of what the buggy code looked like: Runtime ID was not incorporated into the signature context for the shown roothash commitment-verification paths, so the signature domain was not explicitly separated per runtime.

## Search Motifs

- Motif 1: signature verification without signer-set or committee binding
- Motif 2: valid signature reused across runtime, role, or domain scope
- Motif 3: message accepted after verify but before signer authorization

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that something was signed, but did not bind the signature to the correct signer set, runtime, committee, or domain.

## Patch Pattern

- What the fix changed structurally: The fix threads 'runtimeID' into the affected verification paths, derives runtime-qualified signature contexts via 'WithSuffix(runtimeID.String())', updates commitment-generation helpers to sign with an explicit runtime, and adds regression coverage for runtime-mismatched evidence.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
