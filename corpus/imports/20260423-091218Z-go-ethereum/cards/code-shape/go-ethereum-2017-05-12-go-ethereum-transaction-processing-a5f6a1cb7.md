# Code-Shape Card

## Metadata

- ID: `go-ethereum-2017-05-12-go-ethereum-transaction-processing-a5f6a1cb7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-configuration-hardening`

## Code Shape Summary

- The grounded security-relevant change is in params/config.go: ChainConfig.checkCompatible now rejects incompatible MetropolisBlock settings, matching the existing compatibility checks for earlier fork blocks. The evidence supports consensus-configuration hardening, not a confirmed exploitable vulnerability, transaction replay flaw, or VM execution bug.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
