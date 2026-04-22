# Code-Shape Card

## Metadata

- ID: `scroll-2025-11-28-scroll-transaction-processing-752e4e11`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-fee-bounds`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch is security-relevant in theme but not established as a vulnerability fix by the provided evidence. What is directly supported is that the code stopped computing blob base fee locally, switched to querying the L1 node for that value, and added configured caps before relaying fee updates. That is stronger evidence for fee-correctness and liveness hardening than for a confirmed exploitable overflow bug.

## Search Motifs

- Motif 1: local recomputation of canonical chain fee values instead of querying the node
- Motif 2: same fee calculation duplicated across sender, watcher, and relayer paths
- Motif 3: patch adds configured caps before packing or relaying fee update calldata

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Stop computing blob fee locally, query the canonical node for the authoritative value, and cap relayed fee parameters before constructing outbound transactions.

## False Match Warnings

- Warning 1: If downstream contracts or nodes always clamp fee inputs to the same canonical bounds, a similar local fix may be mostly robustness work.
- Warning 2: Metric or logging changes around fees are not the core signal; the key issue is canonical fee sourcing plus upper bounds before relay.
- Warning 3: The evidence supports fee-path hardening, not a proven exploitable overflow.
