# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-06-27-oasis-core-cryptography-ee21c841e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `predictable-beacon-entropy`

## Code Shape Summary

- Short description of what the buggy code looked like: The code suggests that deterministic/debug beacon behavior and the canonical Tendermint beacon path were not previously separated as explicitly as they are after the patch. The scheduler also had a more flexible beacon-backend injection point. That supports a hardening narrative, but the provided excerpts do not prove that the older design was exploitable in production.

## Search Motifs

- Motif 1: parsed descriptor or request missing cross-field invariant checks
- Motif 2: wrong state coordinate compared during validation
- Motif 3: malformed or incomplete input reaches a privileged sink

## Typical Asymmetry

- What was checked in one path but missing in another: A structure or field was parsed and partially checked, but a role-specific, state-specific, or cross-field invariant was still missing.

## Patch Pattern

- What the fix changed structurally: The patch introduces an explicit 'debugDeterministic' flag in the beacon application, warns when that mode is used, adjusts epoch-change logic to distinguish production entropy handling from deterministic behavior, removes the scheduler's injected beacon-backend dependency, and removes a direct ABCI beacon getter in the Tendermint backend.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
