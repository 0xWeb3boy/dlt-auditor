# Code-Shape Card

## Metadata

- ID: `nitro-2022-06-01-nitro-transaction-processing-37c04d56b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `caller-controlled-withdrawal-destination`

## Code Shape Summary

- Short description of what the buggy code looked like: The grounded change is that the validator client no longer accepts or passes a configurable `withdrawDestination` when withdrawing staker funds. That is consistent with hardening a sensitive withdrawal path, but the provided excerpts do not establish a concrete vulnerability, exploit path, or the exact contract-side validation change.

## Search Motifs

- Motif 1: withdraw or sweep APIs expose a free-form destination parameter in privileged contexts
- Motif 2: client structs store withdrawal recipient addresses even though the underlying action should be policy-bound
- Motif 3: sensitive funds movement paths narrow parameters in later patches by deleting rather than validating them

## Typical Asymmetry

- What was checked in one path but missing in another: The code exposed a policy-sensitive parameter or mode choice at a higher layer, even though the underlying action was supposed to be bound to a narrower trusted destination or safer default.

## Patch Pattern

- What the fix changed structurally: Remove a caller-controlled parameter from a privileged path and centralize selection or validation behind a narrower interface.

## False Match Warnings

- What looks similar but is often not a bug: If the destination or mode is deterministically overwritten later, similar parameter flow may be harmless.
