# Code-Shape Card

## Metadata

- ID: `scroll-2025-07-02-scroll-rpc-client-api-adac0404`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verifier-artifact-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The visible patch fixes verifier-tool behavior around verification-key handling and bundle verifier asset export. It corrects an inverted equality check for chunk and batch proofs, forces the bundle path to use the locally selected verifier key, and copies `verifier.bin` during asset export. That is clearly a correctness or hardening change in proof-verification tooling, but the provided evidence does not establish an exploitable vulnerability, a production attack boundary, or any on-chain security impact.

## Search Motifs

- Motif 1: inverted equality check around verification key bytes
- Motif 2: verification tool copies or selects verifier assets from the wrong source bundle
- Motif 3: proof verification path uses one artifact set while export path omits the required verifier binary

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Bind verification runs to the selected verification key, fix inverted artifact-consistency checks, and export the verifier binary required by the chosen proof path.

## False Match Warnings

- Warning 1: If the tooling is purely local and not used as a policy gate, a similar mismatch may remain a correctness issue rather than security hardening.
- Warning 2: Changing file-copy behavior alone is not enough; the security-relevant part is binding the correct verification key and verifier binary to the proof path.
- Warning 3: The evidence supports tool hardening, not a demonstrated production verifier bypass.
