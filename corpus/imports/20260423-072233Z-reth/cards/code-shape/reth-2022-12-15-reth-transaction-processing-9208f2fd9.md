# Code-Shape Card

## Metadata

- ID: `reth-2022-12-15-reth-transaction-processing-9208f2fd9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-selection-logic`

## Code Shape Summary

- The strongest supported finding is a correctness bug in executor configuration: `SpecUpgrades::revm_spec()` used reversed comparisons, so the executor could choose the wrong REVM hardfork rules for a block. The patch also tightens receipt-status derivation so unexpected VM exit reasons become errors instead of being folded into a normal failed receipt. This touches consensus-sensitive code, but the provided evidence does not prove attacker reachability, exploitation, or an observed security incident, so the security classification should be downgraded to unclear.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
