# Code-Shape Card

## Metadata

- ID: `geth-arb-2023-10-13-go-ethereum-storage-f88557d061`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting`

## Code Shape Summary

- Activation consumed gas in a helper path but needed to update the caller-visible gas meter so the consumed amount could not be lost across the boundary.

## Search Motifs

- helper receives gas by value and consumption is not reflected in caller
- activation changes state before gas meter is updated
- metered subroutine returns result but not remaining budget
- attacker-controlled count or loop bound reaches allocation or scheduling
- metadata validation happens after network or storage work is queued
- duplicate, stale, or known items consume work instead of being skipped

## Typical Asymmetry

- The vulnerable asymmetry is cost mismatch: cheap attacker-controlled input could trigger more expensive work at gas burn, activation state, and storage/state commitment before bounds or progress checks ran.

## Patch Pattern

- Pass mutable gas into activation, return the remaining gas, and burn or persist the consumed amount consistently.

## False Match Warnings

- a hard request cap is enforced before allocation or network work
- peer scoring or authentication makes repeated abuse impractical
- the path is operator-only and unreachable from untrusted clients
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
