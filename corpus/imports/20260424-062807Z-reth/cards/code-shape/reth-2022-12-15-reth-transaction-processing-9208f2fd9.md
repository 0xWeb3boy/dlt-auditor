# Code-Shape Card

## Metadata

- ID: `reth-2022-12-15-reth-transaction-processing-9208f2fd9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-selection-logic`

## Code Shape Summary

- The directly supported root cause is a logic error in `SpecUpgrades::revm_spec()`: the fork-activation comparisons were written in the wrong direction. A secondary executor change tightened classification of VM exit reasons so unexpected outcomes are surfaced as errors instead of being collapsed into receipt status.

## Search Motifs

- authenticated trie/proof path drops empty-root, revealed-node, or rollback state needed for valid output
- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- search for `SpecUpgrades::revm_spec()` call sites that derive, cache, or validate security-sensitive state
- fork-selection-logic fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses block or transaction input -> execution-layer validator, but fork-state-consistency is incomplete before the code updates or relies on transaction acceptance or consensus rule application.

## Patch Pattern

- Correct a boundary-condition predicate in a protocol-selection function, then tighten downstream result classification so unexpected execution states are rejected rather than normalized.

## False Match Warnings

- No evidence shows the buggy spec selection was exploitable by an attacker in deployed configurations
- No observed consensus split, chain acceptance failure, or state divergence is documented in the provided material
- No security advisory, vulnerability report, or exploit narrative ties this commit to a concrete security incident
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
