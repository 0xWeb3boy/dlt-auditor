# Code-Shape Card

## Metadata

- ID: `nibiru-2026-01-22-nibiru-rpc-client-api-59336f71`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-nondeterminism`

## Code Shape Summary

- Consensus logic ranged over a Go map while updating oracle validator state and rewards; the fix canonicalized validator address order before all consensus-visible effects.

## Search Motifs

- range over map in BeginBlock/EndBlock/keeper consensus path
- comments mention AppHash mismatch or nondeterminism
- helper returns sorted keys before state writes
- events or rewards emitted from map iteration order

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Extract keys, sort them canonically, and use that ordered list for all state writes, reward calculations, and consensus-visible event emission.

## False Match Warnings

- Map iteration in read-only RPC code is not consensus-critical
- Sorting only for presentation does not fix state write nondeterminism elsewhere
- Need evidence iteration affects writes, events, or app hash
