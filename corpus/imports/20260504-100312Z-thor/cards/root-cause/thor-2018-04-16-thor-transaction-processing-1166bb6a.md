# Root-Cause Card

## Metadata

- ID: `thor-2018-04-16-thor-transaction-processing-1166bb6a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `native-contract-hook-dispatch-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `call-context-gating`

## Violated Invariant

- Invariant: Native contract hooks must run only for direct execution of the native contract code, not when the same code is reached through delegated or code-substituted call contexts.

## Trust Boundary

- Boundary: `contract-call-context->native-hook-dispatch`

## Attack Surface

- Entrypoint type: `state-transition-native-contract-hook`
- Sensitive sink: native contract hook execution with access to EVM state, contract input, gas charging, and log emission
- Attacker capability: Submit or trigger a contract call that reaches native-code dispatch through VM execution.
- Preconditions: The native hook mechanism is enabled for the addressed contract.

## Impact Pattern

- Primary impact: execution-context integrity
- Secondary impact: unauthorized native state transition
- Blast radius: `chain-wide`

## Short Reusable Lesson

- Privileged VM hooks should be dispatched from the execution engine using the active call frame, and should explicitly reject delegated or code-substituted contexts before any native state access.
