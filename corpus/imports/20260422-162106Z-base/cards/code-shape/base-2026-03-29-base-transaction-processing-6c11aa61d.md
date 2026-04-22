# Code-Shape Card

## Metadata

- ID: `base-2026-03-29-base-transaction-processing-6c11aa61d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: Validation logic in this AA transaction path relied on an implicit sender-derived lookup in at least one place and did not yet enforce all of the structural and encoded-size limits that the patched code now requires.

## Search Motifs

- Motif 1: runtime or on-chain policy is read but not enforced before a privileged action
- Motif 2: one execution path applies the environment guard while another path skips it
- Motif 3: local configuration is treated as authoritative even when live chain policy can differ

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed some validation or normalization up front, but a later reuse, reconstruction, or alternate branch could still reach the sink without the exact same property being enforced.

## Patch Pattern

- What the fix changed structurally: Tighten validation by replacing implicit identity use with an explicit validated parameter and by adding earlier structural and size guards on untrusted transaction input.

## False Match Warnings

- What looks similar but is often not a bug: Supported claim: the commit hardens validation and resource limits in a security-sensitive AA transaction path.
