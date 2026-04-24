# Code-Shape Card

## Metadata

- ID: `reth-2026-02-04-reth-transaction-processing-7671838c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## Code Shape Summary

- The root cause was inconsistent handling of two different gas-accounting values after EIP-7778/Amsterdam. Receipt construction and block validation were not clearly carrying and using the protocol-correct value for each purpose, creating a risk that header validation would compare against the wrong gas source.

## Search Motifs

- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- consensus-safety fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses transaction execution/precompile call -> gas accounting state, but protocol-rule-enforcement is incomplete before the code updates or relies on gas reservoir, receipt, and execution accounting.

## Patch Pattern

- Separate protocol meanings that were previously conflated, then thread the correct value through each validation boundary instead of reusing a nearby but semantically different field.

## False Match Warnings

- No failing test, reproducer, or execution trace is provided showing concrete invalid acceptance or rejection before the fix
- No advisory, commit text, or patch evidence states attacker exploitability or an observed chain split
- The excerpt does not prove whether the bug could be triggered by adversarial blocks in practice versus causing compatibility issues at fork activation
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
