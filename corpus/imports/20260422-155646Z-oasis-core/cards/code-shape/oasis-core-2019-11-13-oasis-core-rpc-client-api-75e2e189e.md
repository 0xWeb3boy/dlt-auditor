# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-11-13-oasis-core-rpc-client-api-75e2e189e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-malformed-input`

## Code Shape Summary

- Short description of what the buggy code looked like: Malformed public keys were handled inconsistently across the code path: deserialization allowed a nil/zero-length key as success, but later identity-conversion logic assumed exact key length and could panic when given that malformed value.

## Search Motifs

- Motif 1: parsed descriptor or request missing cross-field invariant checks
- Motif 2: wrong state coordinate compared during validation
- Motif 3: malformed or incomplete input reaches a privileged sink

## Typical Asymmetry

- What was checked in one path but missing in another: A structure or field was parsed and partially checked, but a role-specific, state-specific, or cross-field invariant was still missing.

## Patch Pattern

- What the fix changed structurally: The patch makes 'PublicKey.UnmarshalBinary' fail unless the input length is exactly 'PublicKeySize'. It changes 'ToMapKey' to stop panicking on malformed keys, changes 'MarshalBinary' to serialize malformed keys as an all-zero key documented as blacklisted/invalid, and updates 'VerifyRegisterEntityArgs' to reject malformed node IDs before duplicate detection uses them.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
