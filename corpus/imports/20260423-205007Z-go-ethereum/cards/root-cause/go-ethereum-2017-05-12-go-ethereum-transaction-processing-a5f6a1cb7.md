# Root-Cause Card

## Metadata

- ID: `go-ethereum-2017-05-12-go-ethereum-transaction-processing-a5f6a1cb7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-configuration-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-validation`

## Violated Invariant

- Invariant: A node with an existing local chain should reject a replacement ChainConfig that would change consensus fork boundaries already relevant at the current head. The patch extends that compatibility invariant to MetropolisBlock.

## Trust Boundary

- Boundary: Caller-controlled signing or account-management requests crossing into wallet-held authority.

## Attack Surface

- Entrypoint type: `wallet or signing api`
- Sensitive sink: `transaction or message signing under local account authority`

## Impact Pattern

- Primary impact: `consensus-configuration-mismatch`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The grounded security-relevant change is in params/config.go: ChainConfig.checkCompatible now rejects incompatible MetropolisBlock settings, matching the existing compatibility checks for earlier fork blocks.
