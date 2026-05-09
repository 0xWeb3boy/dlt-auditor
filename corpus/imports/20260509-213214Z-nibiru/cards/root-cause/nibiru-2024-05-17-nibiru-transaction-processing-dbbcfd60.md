# Root-Cause Card

## Metadata

- ID: `nibiru-2024-05-17-nibiru-transaction-processing-dbbcfd60`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-transaction-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `keeper-level basic message validation`

## Violated Invariant

- Invariant: A transaction message must satisfy its basic syntactic and semantic validation before it is converted into an execution object or passed to the state transition engine.

## Trust Boundary

- Boundary: Externally supplied transaction bytes cross from message handling into EVM execution.

## Attack Surface

- Entrypoint type: EVM transaction message handler
- Sensitive sink: transaction conversion and ApplyEvmTx execution

## Impact Pattern

- Primary impact: malformed transaction hardening
- Secondary impact: possible crash or inconsistent execution if downstream assumptions are violated

## Short Reusable Lesson

- A state-changing transaction handler added an explicit basic-validation gate before converting and executing a foreign-runtime transaction.
