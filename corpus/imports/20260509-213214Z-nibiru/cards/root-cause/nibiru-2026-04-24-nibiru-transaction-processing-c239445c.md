# Root-Cause Card

## Metadata

- ID: `nibiru-2026-04-24-nibiru-transaction-processing-c239445c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-vm-callback-guard`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `callback-context validation`

## Violated Invariant

- Invariant: Mutable native precompile methods must reject calls made while execution is inside a VM-originated contract callback or module-caller context.

## Trust Boundary

- Boundary: User-controlled EVM contract callback crosses into native precompile methods that can mutate bank, bridge, or Wasm state.

## Attack Surface

- Entrypoint type: mutable EVM precompile call during ERC20/module-originated callback
- Sensitive sink: FunToken sendToEvm and Wasm execute native state transitions

## Impact Pattern

- Primary impact: privileged callback context abuse
- Secondary impact: native state mutation from unexpected VM context

## Short Reusable Lesson

- Mutable precompile handlers lacked an execution-context guard and could be reached while the SDK context indicated a VM-originated callback.
