# Code-Shape Card

## Metadata

- ID: `base-2026-03-05-base-storage-fcefb853a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: According to the commit body, the initial validator implementation did not enforce all structural and arithmetic preconditions before iterating checkpoints and did not fully cross-check externally supplied header data. That created a risk that malformed inputs could alter or truncate validation instead of causing an immediate failure.

## Search Motifs

- Motif 1: cache or retry reuse happens without rechecking canonical chain state
- Motif 2: request identity is treated as sufficient even though the historical state coordinate can change
- Motif 3: stale checkpoint, execution, or proof data is reused across parent-context changes

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that an existing request or cache entry matched a local identifier, but did not recheck that the cached state still matched the canonical chain state being acted on.

## Patch Pattern

- What the fix changed structurally: Add fail-closed input validation around security-sensitive verification logic: check expected counts before iterating, use checked arithmetic for attacker-influenced counters, reject degenerate parameters early, and verify consistency of externally supplied metadata before trusting it.

## False Match Warnings

- What looks similar but is often not a bug: Treat this as challenger-side validation hardening, not a confirmed consensus-break or fund-loss bug.
