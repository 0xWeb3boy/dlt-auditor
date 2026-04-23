# Root-Cause Card

## Metadata

- ID: `go-ethereum-2017-05-12-go-ethereum-transaction-processing-a5f6a1cb7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-configuration-hardening`
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

- The grounded security-relevant change is in params/config.go: ChainConfig.checkCompatible now rejects incompatible MetropolisBlock settings, matching the existing compatibility checks for earlier fork blocks. The evidence supports consensus-configuration hardening, not a confirmed exploitable vulnerability, transaction replay flaw, or VM execution bug.
