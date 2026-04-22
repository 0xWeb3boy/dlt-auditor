# Code-Shape Card

## Metadata

- ID: `oasis-core-2018-05-26-oasis-core-cryptography-19cd4a286`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signed-message-validation-consistency`

## Code Shape Summary

- Short description of what the buggy code looked like: The code previously did not consistently carry one verified signed representation through later processing. The patch indicates that signed payload handling relied on extracted or reconstructed values in some paths instead of preserving and reusing the verified wrapper end to end.

## Search Motifs

- Motif 1: signature verification without signer-set or committee binding
- Motif 2: valid signature reused across runtime, role, or domain scope
- Motif 3: message accepted after verify but before signer authorization

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that something was signed, but did not bind the signature to the correct signer set, runtime, committee, or domain.

## Patch Pattern

- What the fix changed structurally: The fix restructures signed-message handling so the signed wrapper stores serialized payload bytes, the dispatcher uses the verified call object for both method lookup and execution, and one registry identity check now treats payload extraction as fallible.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
