# Code-Shape Card

## Metadata

- ID: `base-2026-03-22-base-consensus-424476a9d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## Code Shape Summary

- Short description of what the buggy code looked like: The start path accepted activation without enforcing that the execution engine had a valid current unsafe head, and the supplied `unsafe_head` was not shown to influence the transition before activation. Separate state-publication timing also meant callers could continue observing a zero unsafe head until later engine activity, making invalid start requests more likely.

## Search Motifs

- Motif 1: latest observed head is forwarded directly despite a configured confirmation-delay policy
- Motif 2: startup or wake-up logic trusts requested state before confirming the engine or source state is initialized
- Motif 3: policy values are logged or stored but not enforced consistently on downstream reads

## Typical Asymmetry

- What was checked in one path but missing in another: The code distinguished between observed head state and safer delayed or initialized state in one place, but another path still consumed the fresher or unchecked state directly.

## Patch Pattern

- What the fix changed structurally: Validate engine state at the activation boundary, fail closed on uninitialized or inconsistent state, and publish the authoritative state early enough that callers can satisfy the new preconditions.

## False Match Warnings

- What looks similar but is often not a bug: Supported claim: the patch hardens a consensus-sensitive activation path by enforcing engine-state validation before starting the sequencer.
