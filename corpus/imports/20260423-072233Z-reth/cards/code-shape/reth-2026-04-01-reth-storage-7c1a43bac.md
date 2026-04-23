# Code-Shape Card

## Metadata

- ID: `reth-2026-04-01-reth-storage-7c1a43bac`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-state-reuse`

## Code Shape Summary

- A precompile cache hit reused a cached output object that embedded stale gas and reservoir state. The patch passes the current caller gas and reservoir into reconstruction and reuses only stable cached output data and regular gas cost.

## Search Motifs

- cache hit returns cloned output with GasTracker
- cached result includes reservoir or state_gas_spent
- to_result helper lacks current gas limit parameter

## Typical Asymmetry

- The code has one path that performs the expected validation, accounting, or quality update while a nearby special-case, cache-hit, early-return, or alternate response path omits it.

## Patch Pattern

- Split stable cached result data from invocation-local accounting and rebuild the accounting object from the current call frame on every cache hit.

## False Match Warnings

- Pure output-byte caching is fine when live accounting is reconstructed.
- Need evidence of attacker-controlled cache hits before claiming exploitability.
- No consensus-impact claim without divergent execution results or invalid block behavior.
