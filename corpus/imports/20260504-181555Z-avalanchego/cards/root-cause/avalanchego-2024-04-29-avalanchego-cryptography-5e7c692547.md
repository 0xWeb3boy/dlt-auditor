# Root-Cause Card

## Metadata

- ID: `avalanchego-2024-04-29-avalanchego-cryptography-5e7c692547`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-header-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fork-dependent-header-field-validation`

## Violated Invariant

- Invariant: Block header fields introduced or removed by a fork must be accepted, rejected, or required according to the active fork rules.

## Trust Boundary

- Boundary: Peer-supplied EVM block headers cross into syntactic block validation.

## Attack Surface

- Entrypoint type: EVM block/header syntactic verification
- Sensitive sink: block acceptance under fork-specific header rules

## Impact Pattern

- Primary impact: protocol-validity, consensus-integrity
- Secondary impact: medium_high_integrity

## Root Cause

- The grounded issue is an incomplete fork-dependent header-field validation check for ParentBeaconRoot in the EVM syntactic verification path. The evidence does not support stronger claims such as state corruption, cryptographic failure, or proven consensus divergence. ## Walkthrough 1. A block header reaches blockValidator.SyntacticVerify in plugin/evm/block_verification.go. 2.

## Short Reusable Lesson

- Fork-aware header validation was expanded to cover a previously incomplete field check. The reusable shape is block syntactic validation where each fork-dependent field needs explicit nil/value handling on both sides of activation.
