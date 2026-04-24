# Code-Shape Card

## Metadata

- ID: `bor-2024-09-05-bor-transaction-processing-8262eae9e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-context-mismatch`

## Code Shape Summary

- The patch corrects a state-selection mismatch in Bor's LastStateId read path by switching from a generic Call(...) helper to CallWithState(...) and threading the provided state through to execution. The evidence supports a real correctness fix in a consensus-adjacent path, but it does not establish a concrete security vulnerability, exploit path, or demonstrated consensus failure. Root cause: An API layering mismatch: the Bor code needed a read bound to a specific state.StateDB, but it used a convenience wrapper that discarded that state and defaulted to a different execution context.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses external RPC client to node service boundary and reaches backend state access, privileged API behavior, or response serialization before the missing property is enforced.

## Patch Pattern

- Replace a convenience API that silently uses default context with an explicit API that requires the caller to pass the intended state and block context.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
