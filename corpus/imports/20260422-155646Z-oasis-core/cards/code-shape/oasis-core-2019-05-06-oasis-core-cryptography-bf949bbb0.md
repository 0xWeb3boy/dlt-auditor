# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-05-06-oasis-core-cryptography-bf949bbb0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The only grounded issue visible in the provided diff is that this scheduler path previously consumed runtime capability metadata with weaker local validation. The stronger claim that the system as a whole lacked attestation verification is not established from the provided evidence, because earlier registration-time or other validation is not shown.

## Search Motifs

- Motif 1: parsed descriptor or request missing cross-field invariant checks
- Motif 2: wrong state coordinate compared during validation
- Motif 3: malformed or incomplete input reaches a privileged sink

## Typical Asymmetry

- What was checked in one path but missing in another: A structure or field was parsed and partially checked, but a role-specific, state-specific, or cross-field invariant was still missing.

## Patch Pattern

- What the fix changed structurally: The scheduler node-list builder was tightened so that unknown runtimes are skipped, TEE hardware classification starts from an invalid default, and TEE capability objects are locally verified with caps.Verify(ts) before their metadata is used.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
