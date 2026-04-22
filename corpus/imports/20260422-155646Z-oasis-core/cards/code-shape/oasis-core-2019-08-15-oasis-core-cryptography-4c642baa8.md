# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-08-15-oasis-core-cryptography-4c642baa8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: Incomplete role-specific validation in the registry registration path: the validator role could be declared without enforcing the presence of consensus addresses.

## Search Motifs

- Motif 1: parsed descriptor or request missing cross-field invariant checks
- Motif 2: wrong state coordinate compared during validation
- Motif 3: malformed or incomplete input reaches a privileged sink

## Typical Asymmetry

- What was checked in one path but missing in another: A structure or field was parsed and partially checked, but a role-specific, state-specific, or cross-field invariant was still missing.

## Patch Pattern

- What the fix changed structurally: The registry validation function was tightened so a node claiming the validator role must provide non-empty consensus addresses; otherwise registration fails with 'ErrInvalidArgument'. The TLS-related code was also refactored to separate certificate creation from saving, but that change is not supported as the root security mechanism by the provided evidence.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
