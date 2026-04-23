# Code-Shape Card

## Metadata

- ID: `nitro-2022-03-17-nitro-transaction-processing-c4a31f084`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reorg-state-mismatch`

## Code Shape Summary

- Short description of what the buggy code looked like: This patch is best supported as security hardening in validator reorg handling. The code adds and checks validated block hashes so the validator does not keep operating from a stale validated height after the canonical chain changes at the same block number.

## Search Motifs

- Motif 1: resume logic persists a height or index without the associated block hash
- Motif 2: same-height reorg handling is missing from recovery code
- Motif 3: restored validator state is trusted after restart without chain-identity revalidation

## Typical Asymmetry

- What was checked in one path but missing in another: A cached, implicit, or convenience state source was accepted as if it were canonical, while the later sink depended on stronger identity, boundary, or chain-binding guarantees that were not actually enforced there.

## Patch Pattern

- What the fix changed structurally: Persist the chain identity hash alongside the progress index, then fail closed whenever resumed or derived validator state does not match the live canonical chain.

## False Match Warnings

- What looks similar but is often not a bug: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
