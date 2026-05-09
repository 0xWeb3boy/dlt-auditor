# Code-Shape Card

## Metadata

- ID: `nibiru-2024-10-26-nibiru-transaction-processing-c6249126`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `precompile-rollback-hardening`

## Code Shape Summary

- Precompile multistore snapshots were moved into the main transaction journal and tied to the EVM transaction context to preserve atomic rollback semantics.

## Search Motifs

- precompile snapshots stored outside StateDB journal
- synthetic state object for native side effects
- commit uses ctx instead of evmTxCtx
- revert path handles EVM journal but not native cache

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Record native precompile snapshots as journal entries, propagate snapshot errors, and use the same transaction context for reads, commits, and rollbacks.

## False Match Warnings

- Do not flag read-only precompiles
- Need a state-changing native side effect plus possible revert/error path
- Mere refactoring of context plumbing is not enough without rollback semantics
