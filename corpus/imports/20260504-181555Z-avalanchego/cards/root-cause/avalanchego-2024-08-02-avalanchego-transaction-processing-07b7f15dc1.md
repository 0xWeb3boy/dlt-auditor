# Root-Cause Card

## Metadata

- ID: `avalanchego-2024-08-02-avalanchego-transaction-processing-07b7f15dc1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invalid-header-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `local-protocol-header-invariant`

## Violated Invariant

- Invariant: Header validation must enforce local chain invariants even when the upstream fork format permits a broader field domain.

## Trust Boundary

- Boundary: Peer-supplied Cancun/EIP-4844-style headers cross into Avalanche EVM block validation.

## Attack Surface

- Entrypoint type: EVM block/header syntactic verification
- Sensitive sink: acceptance of a block header violating the local no-blobs rule

## Impact Pattern

- Primary impact: consensus-integrity, protocol-validity
- Secondary impact: medium_high_integrity

## Root Cause

- The Cancun header validation logic did not fully encode Avalanche's local protocol rule that blobs are disabled. Generic Cancun/EIP-4844 field-shape validation was present, but the Avalanche-specific zero BlobGasUsed invariant was missing from the shown acceptance paths. ## Walkthrough 1. A Cancun-era block header reaches EVM syntactic verification. 2.

## Short Reusable Lesson

- Header validation now rejects positive BlobGasUsed despite generic Cancun field support. The reusable shape is a chain-specific invariant layered on top of inherited fork-format validation.
