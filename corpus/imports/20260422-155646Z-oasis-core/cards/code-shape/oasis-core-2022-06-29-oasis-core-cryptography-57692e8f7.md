# Code-Shape Card

## Metadata

- ID: `oasis-core-2022-06-29-oasis-core-cryptography-57692e8f7`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-query-verification`

## Code Shape Summary

- Short description of what the buggy code looked like: Historical-query handling did not have a clearly enforced verification step in the shown interface/dispatch path, so query consumers could rely on weaker validation than the normal verifier path. The evidence supports missing or insufficient query-time binding checks, not stronger claims such as signature bypass or replay exploitation.

## Search Motifs

- Motif 1: signature verification without signer-set or committee binding
- Motif 2: valid signature reused across runtime, role, or domain scope
- Motif 3: message accepted after verify but before signer authorization

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that something was signed, but did not bind the signature to the correct signer set, runtime, committee, or domain.

## Patch Pattern

- What the fix changed structurally: The fix adds 'verify_for_query' to the verifier trait, implements it in the Tendermint verifier, routes query-mode requests through that path, and adds an explicit runtime-ID/namespace check before query-time consensus state is returned or treated as verified.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
