# Validation Card

## Metadata

- ID: `nitro-2022-04-10-nitro-transaction-processing-3a9ee3753`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `artifact-identity-check`

## What Confirmed The Issue

- Evidence 1: The patch adds explicit module-root canonicalization and a root-match check when loading validator machines, and it wires staker initialization through loader-based latest-root update logic.
- Evidence 2: Canonicalize alias inputs first, then validate the loaded artifact's reported identity against the canonical value before accepting it.

## What Could Have Invalidated It

- Compensating control 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Compensating control 2: If the path is test-only or offline tooling only, treat similar issues as lower-severity hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Caution 2: Do not claim chain-wide divergence without evidence that the wrong state can be persisted, signed, or submitted onward.
