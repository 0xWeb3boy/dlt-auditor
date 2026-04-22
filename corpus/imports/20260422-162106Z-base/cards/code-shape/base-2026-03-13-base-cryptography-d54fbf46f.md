# Code-Shape Card

## Metadata

- ID: `base-2026-03-13-base-cryptography-d54fbf46f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-integrity`

## Code Shape Summary

- Short description of what the buggy code looked like: At most, the evidence suggests the earlier design used a more flexible configuration path instead of clearly deriving and pinning enclave parameters from canonical per-chain data. The provided material does not prove that this flexibility created an actual vulnerability in production or that untrusted parties could control the old configuration source.

## Search Motifs

- Motif 1: verification result is partially interpreted instead of requiring explicit success
- Motif 2: one proof element or branch is trusted without recomputing the canonical expected value
- Motif 3: validation logic treats malformed or mismatched proof structure as recoverable instead of rejecting it

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed some validation or normalization up front, but a later reuse, reconstruction, or alternate branch could still reach the sink without the exact same property being enforced.

## Patch Pattern

- What the fix changed structurally: Replace a flexible configuration path with deterministic derivation of per-chain values from canonical rollup data, pin expected hashes for a fixed supported-chain set, and make unknown chain IDs fail explicitly.

## False Match Warnings

- What looks similar but is often not a bug: Supported: the patch hardens enclave configuration selection and supported-chain enforcement.
