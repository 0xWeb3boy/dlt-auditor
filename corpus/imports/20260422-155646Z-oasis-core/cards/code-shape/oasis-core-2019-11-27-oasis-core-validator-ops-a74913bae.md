# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-11-27-oasis-core-validator-ops-a74913bae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-debug-configuration`

## Code Shape Summary

- Short description of what the buggy code looked like: A missing sanity check allowed an unsafe configuration mode to be selected in the entity load/generation path without the explicit debug acknowledgement now required by the patch. The provided evidence does not show whether this was exploitable beyond local operator misconfiguration.

## Search Motifs

- Motif 1: parsed descriptor or request missing cross-field invariant checks
- Motif 2: wrong state coordinate compared during validation
- Motif 3: malformed or incomplete input reaches a privileged sink

## Typical Asymmetry

- What was checked in one path but missing in another: A structure or field was parsed and partially checked, but a role-specific, state-specific, or cross-field invariant was still missing.

## Patch Pattern

- What the fix changed structurally: The patch inserts an early sanity check in 'loadOrGenerateEntity' that blocks 'AllowEntitySignedNodes' unless the unsafe debug flag is set. The remaining provided hunks rename constants used by registry CLI code.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
