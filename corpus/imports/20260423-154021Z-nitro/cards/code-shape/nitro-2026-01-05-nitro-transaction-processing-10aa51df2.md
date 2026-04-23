# Code-Shape Card

## Metadata

- ID: `nitro-2026-01-05-nitro-transaction-processing-10aa51df2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-validation-recording`

## Code Shape Summary

- Short description of what the buggy code looked like: The grounded change is that MEL extraction now records tx-indexed logs when consuming certain parent-chain logs, and aborts if that recording fails. That supports later MEL validation, but the provided evidence does not establish a concrete vulnerability, exploit path, or prior security bypass.

## Search Motifs

- Motif 1: extractors consume logs but do not persist the per-tx witness data required by validators
- Motif 2: recording errors are ignored on paths that later assume the witness exists
- Motif 3: later fixes make log or witness recording a hard requirement instead of best effort

## Typical Asymmetry

- What was checked in one path but missing in another: The code treated cached, lazily created, or non-finalized state as if it were authoritative, while later validation or cleanup logic depended on stronger finalized-state guarantees.

## Patch Pattern

- What the fix changed structurally: Make witness-recording mandatory at the point where relevant logs are consumed, and treat recording failure as a hard error.

## False Match Warnings

- What looks similar but is often not a bug: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
