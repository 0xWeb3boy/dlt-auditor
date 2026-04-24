# Root-Cause Card

## Metadata

- ID: `sei-chain-2021-04-12-sei-chain-rpc-client-api-2a4fd03c4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `failed-ack-state-rollback`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `transactional-callback-commit`

## Violated Invariant

- Invariant: Application callback state changes must commit only when the enclosing protocol operation accepts the result they correspond to.

## Trust Boundary

- Boundary: IBC packet data and module callback result -> core channel state transition

## Attack Surface

- Entrypoint type: cross-chain-packet-handler
- Sensitive sink: committing packet acknowledgement and application callback state

## Impact Pattern

- Primary impact: state-consistency
- Secondary impact: protocol-invariant-enforcement

## Short Reusable Lesson

- Run application callbacks in a cached or transactional context, then commit callback mutations only after checking the protocol-level success signal. Prevents failed synchronous acknowledgements from committing application callback mutations. Clarifies the distinction between packet receipt, acknowledgement writing, and application state commits.
