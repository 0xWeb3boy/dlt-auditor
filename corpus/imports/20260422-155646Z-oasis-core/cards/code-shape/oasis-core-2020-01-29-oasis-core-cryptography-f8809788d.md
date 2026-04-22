# Code-Shape Card

## Metadata

- ID: `oasis-core-2020-01-29-oasis-core-cryptography-f8809788d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: Incomplete registry admission sanity checks: some descriptor constraints were either not enforced in the shown path or were only checked after insufficient context had been assembled.

## Search Motifs

- Motif 1: parsed descriptor or request missing cross-field invariant checks
- Motif 2: wrong state coordinate compared during validation
- Motif 3: malformed or incomplete input reaches a privileged sink

## Typical Asymmetry

- What was checked in one path but missing in another: A structure or field was parsed and partially checked, but a role-specific, state-specific, or cross-field invariant was still missing.

## Patch Pattern

- What the fix changed structurally: The patch adds explicit node-role checks for advertised runtime kinds, explicit non-zero group-size checks for compute runtimes, and a second validation phase that uses a built runtime lookup to re-check compute runtime references.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
