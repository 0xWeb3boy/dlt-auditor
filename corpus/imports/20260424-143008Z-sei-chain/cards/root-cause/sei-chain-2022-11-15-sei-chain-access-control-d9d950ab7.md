# Root-Cause Card

## Metadata

- ID: `sei-chain-2022-11-15-sei-chain-access-control-d9d950ab7`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `ownership-authorization`

## Violated Invariant

- Invariant: State-changing registration or configuration must be authorized against canonical ownership metadata, not only request-declared identity.

## Trust Boundary

- Boundary: externally submitted module message -> privileged contract registration state

## Attack Surface

- Entrypoint type: message-server-handler
- Sensitive sink: registering a contract or changing module-scoped permissions

## Impact Pattern

- Primary impact: privilege-misuse
- Secondary impact: protocol-state-integrity

## Short Reusable Lesson

- Authorize state-changing registration against canonical ownership metadata from the wasm subsystem before accepting DEX registration state. Prevents a non-creator from registering a wasm contract into the DEX through this message path. Bases authorization on wasm module state rather than caller-supplied registration data.
