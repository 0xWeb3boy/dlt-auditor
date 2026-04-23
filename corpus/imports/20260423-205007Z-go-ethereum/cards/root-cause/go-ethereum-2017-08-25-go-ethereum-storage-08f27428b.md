# Root-Cause Card

## Metadata

- ID: `go-ethereum-2017-08-25-go-ethereum-storage-08f27428b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `contract-address-collision`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-transition-consistency`

## Violated Invariant

- Invariant: EVM contract creation should fail when the deterministic CREATE destination is already occupied, evidenced here by a nonzero nonce or a non-empty deployed code hash.

## Trust Boundary

- Boundary: External block or header data crossing into canonical-chain validation and state-transition logic.

## Attack Surface

- Entrypoint type: `block or header validation path`
- Sensitive sink: `consensus-visible state transition or journal replay`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The patch implements Metropolis EIP 684 behavior in go-ethereum's EVM CREATE path by rejecting contract creation when the computed destination address already appears occupied.
