# Code-Shape Card

## Metadata

- ID: `base-2026-04-20-base-transaction-processing-88b36d5a2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-runtime-guard`

## Code Shape Summary

- Short description of what the buggy code looked like: Fork-specific gas-limit policy for Base V1/Azul was omitted from the duplicated inline `CfgEnv` construction paths, so some execution environments could be built without the fork-specific cap even when the timestamp-selected rules were active.

## Search Motifs

- Motif 1: runtime or on-chain policy is read but not enforced before a privileged action
- Motif 2: one execution path applies the environment guard while another path skips it
- Motif 3: local configuration is treated as authoritative even when live chain policy can differ

## Typical Asymmetry

- What was checked in one path but missing in another: One path read or knew the live runtime policy, but the privileged action could still proceed using local assumptions or an alternate path that did not enforce that policy.

## Patch Pattern

- What the fix changed structurally: Centralize duplicated runtime-environment construction and attach fork-conditional parameters in the shared builder, then add a regression test for the fork-specific invariant.

## False Match Warnings

- What looks similar but is often not a bug: The evidence supports a missing fork-specific gas-limit guard in some EVM environment builders.
