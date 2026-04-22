# Code-Shape Card

## Metadata

- ID: `oasis-core-2023-02-01-oasis-core-rpc-client-api-8eabf0d47`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: Committee construction validated only a first matching runtime registration instead of validating every supported key manager runtime version advertised by the node against the same status fields.

## Search Motifs

- Motif 1: parsed descriptor or request missing cross-field invariant checks
- Motif 2: wrong state coordinate compared during validation
- Motif 3: malformed or incomplete input reaches a privileged sink

## Typical Asymmetry

- What was checked in one path but missing in another: A structure or field was parsed and partially checked, but a role-specific, state-specific, or cross-field invariant was still missing.

## Patch Pattern

- What the fix changed structurally: The fix changes 'generateStatus' so committee admission no longer trusts the first matching runtime registration. Instead, it carries the relevant status fields into a loop over all of the node's runtime entries, counts supported versions, and only admits the node when every supported key manager runtime version matches the expected status.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
