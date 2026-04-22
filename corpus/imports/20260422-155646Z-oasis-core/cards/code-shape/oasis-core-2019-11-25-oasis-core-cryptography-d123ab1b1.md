# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-11-25-oasis-core-cryptography-d123ab1b1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-identity-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The registration code was assembling node descriptors with weaker coupling between advertised roles and role-specific fields, and it did not explicitly reject validator consensus addresses whose embedded identity was invalid before building the registration payload.

## Search Motifs

- Motif 1: parsed descriptor or request missing cross-field invariant checks
- Motif 2: wrong state coordinate compared during validation
- Motif 3: malformed or incomplete input reaches a privileged sink

## Typical Asymmetry

- What was checked in one path but missing in another: A structure or field was parsed and partially checked, but a role-specific, state-specific, or cross-field invariant was still missing.

## Patch Pattern

- What the fix changed structurally: The fix makes role handling explicit in the registration worker, adds roles to the descriptor before applying the corresponding hook, gates committee-address registration on role requirements, and filters validator consensus addresses so entries with invalid IDs are dropped before address verification.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
