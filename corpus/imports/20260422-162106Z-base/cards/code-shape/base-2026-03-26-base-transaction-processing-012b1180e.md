# Code-Shape Card

## Metadata

- ID: `base-2026-03-26-base-transaction-processing-012b1180e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proof-claim-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The proof client relied on a weaker proxy invariant, output-root equality, instead of validating the claim against the canonical protocol state: the claimed L2 block number relative to the safe head.

## Search Motifs

- Motif 1: verification result is partially interpreted instead of requiring explicit success
- Motif 2: one proof element or branch is trusted without recomputing the canonical expected value
- Motif 3: validation logic treats malformed or mismatched proof structure as recoverable instead of rejecting it

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed some validation or normalization up front, but a later reuse, reconstruction, or alternate branch could still reach the sink without the exact same property being enforced.

## Patch Pattern

- What the fix changed structurally: Replace indirect equality-based detection with explicit validation against protocol state, and add a dedicated zero-step rule for the safe-head case.

## False Match Warnings

- What looks similar but is often not a bug: Validated as a security fix only for the proof-client claim-validation change in `crates/proof/client/src/prologue.rs`.
