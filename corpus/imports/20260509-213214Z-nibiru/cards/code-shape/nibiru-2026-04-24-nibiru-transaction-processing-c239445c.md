# Code-Shape Card

## Metadata

- ID: `nibiru-2026-04-24-nibiru-transaction-processing-c239445c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-vm-callback-guard`

## Code Shape Summary

- Mutable precompile handlers lacked an execution-context guard and could be reached while the SDK context indicated a VM-originated callback.

## Search Motifs

- delegatecall or callback into precompile during ERC20 transfer
- IsVMSenderCtx guard added before mutable method parsing
- method disabled during EVM-originated contract callback
- precompile send/execute callable from module-originated contract code

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Add a shared callback-context guard and invoke it at the top of every mutable precompile method before parsing inputs or touching native state.

## False Match Warnings

- Read-only precompile methods may be safe in callback context
- Do not claim fund theft without a demonstrated privileged sink and preserved caller
- Revert-reason propagation is support behavior, not the root issue
