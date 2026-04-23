# Code-Shape Card

## Metadata

- ID: `go-ethereum-2026-03-04-go-ethereum-storage-6d99759f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-persistent-state-side-effect`

## Code Shape Summary

- The patch separates read-only execution from persistent writes in go-ethereum's block execution path. The evidence supports that the debug ExecutionWitness RPC path could previously execute through ProcessBlock with setHead=false while still reaching writeBlockWithState, and the patch gates those writes behind an explicit WriteState option. The provided evidence does not establish exploitability, consensus impact, or a concrete security vulnerability, so this should not be kept as a confirmed security fix.

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
