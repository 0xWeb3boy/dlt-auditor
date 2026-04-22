# Code-Shape Card

## Metadata

- ID: `oasis-core-2021-01-21-oasis-core-staking-253376f8d`
- Bug family: `staking_registry_and_accountability`
- Bug class: `insufficient-validator-slashing-enforcement`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence supports an incomplete or brittle slashing/accounting implementation: policy fields and parsing were missing from the shown registration/API paths, and the slashing/fund-transfer code handled zero-funds cases harshly. The evidence does not prove a stronger root cause such as successful acceptance of incorrect results.

## Search Motifs

- Motif 1: stake, slashing, or liveness rule missing on an edge path
- Motif 2: validator or committee accounting uses the wrong role coordinate
- Motif 3: reserved or punishable state treated like ordinary state

## Typical Asymmetry

- What was checked in one path but missing in another: Economic or accountability rules existed in the design, but an edge path failed to enforce them for the affected actor, role, or transition.

## Patch Pattern

- What the fix changed structurally: The patch wires per-runtime slashing settings into runtime configuration and API validation, then adjusts slashing and transfer helpers so stale-evidence or empty-pool cases do not abort the operation path. The visible changes look like support and robustness work for runtime slashing rather than standalone proof of an exploitable bug.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
