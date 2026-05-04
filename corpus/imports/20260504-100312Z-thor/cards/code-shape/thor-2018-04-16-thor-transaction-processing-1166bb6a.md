# Code-Shape Card

## Metadata

- ID: `thor-2018-04-16-thor-transaction-processing-1166bb6a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `native-contract-hook-dispatch-hardening`

## Code Shape Summary

- VM/native-hook dispatch used decomposed call parameters instead of the authoritative active contract object; the fix gates hook execution on direct code execution and passes the EVM/Contract context into the hook.

## Search Motifs

- native hook invoked before checking CodeAddr == Address
- CALLCODE or DELEGATECALL path can reach privileged native handler
- precompile/native bridge receives caller/input/address as separate parameters
- contract input copied into native bridge outside interpreter dispatch guard

## Typical Asymmetry

- The external or cross-context input is treated as already safe, while the later privileged sink assumes that admission, domain, or cardinality checks already happened upstream.

## Patch Pattern

- Move hook dispatch to the interpreter boundary, bind it to the active Contract object, reject delegated/code-substituted contexts, and convert hook argument failures into VM errors.

## False Match Warnings

- No issue if native hooks are unreachable from delegated calls.
- No issue if the hook is read-only and cannot mutate privileged state.
- Treat broad VM refactors as false positives unless they add or remove a concrete dispatch gate.
