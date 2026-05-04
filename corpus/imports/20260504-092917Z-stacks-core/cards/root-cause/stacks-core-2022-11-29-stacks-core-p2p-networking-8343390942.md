# Root-Cause Card

## Metadata

- ID: `stacks-core-2022-11-29-stacks-core-p2p-networking-8343390942`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unhandled-protocol-error-panic`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-bounds-and-error-containment`

## Violated Invariant

- Invariant: Untrusted inputs and execution paths must be bounded and must fail closed without panics, unmetered work, or inconsistent accounting.

## Trust Boundary

- Boundary: Remote peer message crosses into networking, relay, or peer-state validation.

## Attack Surface

- Entrypoint type: `p2p_message_or_block`
- Sensitive sink: peer relay buffer, block acceptance path, or network reputation state

## Impact Pattern

- Primary impact: liveness
- Secondary impact: denial-of-service

## Short Reusable Lesson

- The patch fixes an unhandled PoX already-locked error in Clarity special contract-call handling. Before the change, `ChainstateError::PoxAlreadyLocked` from PoX v1 or PoX v2 lock application had no dedicated match arm and could fall through to the generic `panic!` branch. After the change, both handlers translate the condition into `Error::Runtime(RuntimeErrorType::PoxAlreadyLocked, None)`, and a regression test covers stacking in both PoX versions.
