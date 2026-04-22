# Code-Shape Card

## Metadata

- ID: `base-2024-11-06-base-transaction-processing-9200d03dc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection-state-inconsistency`

## Code Shape Summary

- Short description of what the buggy code looked like: The root cause shown by the provided material is an internal representation problem: replay/protection-related legacy transaction semantics were split across separate fields and a later reconstruction step, allowing inconsistent combinations to exist in memory. A secondary issue was duplicated deposit decode logic instead of a single canonical RLP decode entrypoint.

## Search Motifs

- Motif 1: manual proof or signature byte assembly duplicated across producer and verifier paths
- Motif 2: signature shape or parity is reconstructed after decode instead of validated canonically
- Motif 3: accepted input depends on signer or signature fields that are not bound consistently end to end

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that signature material existed, but did not keep one canonical encoding and validation rule bound to the later sink on every path.

## Patch Pattern

- What the fix changed structurally: Bind related serialized fields together earlier, remove post-hoc reconstruction of derived signature state, and route decoding through a single canonical parser with structural checks.

## False Match Warnings

- What looks similar but is often not a bug: Supported claim: the patch hardens replay-sensitive transaction representation and decoding invariants.
