# Code-Shape Card

## Metadata

- ID: `nibiru-2026-04-27-nibiru-transaction-processing-7395c52e`
- Bug family: `authz_and_role_gates`
- Bug class: `callback-context-access-control`

## Code Shape Summary

- Mutable precompile methods added an explicit VM-sender guard so callback-originated execution cannot reach native state-changing logic.

## Search Motifs

- assertNotVMCaller added to sendToEvm or execute
- IsVMSenderCtx checked after readonly check
- delegatecall security patch for precompiles
- callback context error for mutable method

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Treat callback context as an authorization dimension and deny mutable native precompile methods when that context indicates VM/module-originated execution.

## False Match Warnings

- Do not flag query/view precompiles that cannot mutate state
- Need evidence the context flag corresponds to privileged/module-originated execution
- Avoid duplicate findings when the same commit already covers the same guard
