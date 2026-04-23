# Root-Cause Card

## Metadata

- ID: `go-ethereum-2017-08-25-go-ethereum-storage-08f27428b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `contract-address-collision`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch implements Metropolis EIP 684 behavior in go-ethereum's EVM CREATE path by rejecting contract creation when the computed destination address already appears occupied. The evidence supports a protocol-semantics/state-integrity change, but it does not establish an exploitable vulnerability or a concrete security fix in released deployments.
