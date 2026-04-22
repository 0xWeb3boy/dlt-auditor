# Code-Shape Card

## Metadata

- ID: `base-2026-02-18-base-transaction-processing-0127d7834`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The validator was using incomplete information and a coarse proxy. It relied on account metadata (`bytecode_hash`) plus transaction type instead of inspecting the sender's actual bytecode, and the metering caller did not previously provide that bytecode to the validator.

## Search Motifs

- Motif 1: externally supplied structured data is accepted after only partial validation
- Motif 2: one representation is checked while a different reconstructed or cached representation reaches the sink
- Motif 3: exact consumption, identity binding, or state-coordinate consistency is not rechecked before execution

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed some validation or normalization up front, but a later reuse, reconstruction, or alternate branch could still reach the sink without the exact same property being enforced.

## Patch Pattern

- What the fix changed structurally: Pass concrete execution-relevant state into validation and enforce the narrower invariant directly, instead of inferring it from indirect metadata.

## False Match Warnings

- What looks similar but is often not a bug: Supported: the commit hardens signer validation for EIP-7702-related bytecode handling in the client metering path.
