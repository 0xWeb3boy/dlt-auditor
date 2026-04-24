# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-12-03-sei-chain-staking-b5f8936e8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-nondeterminism-hardening`

## Code Shape Summary

- Likely security fix for consensus nondeterminism in Sei EVM precompile error handling. The provided test evidence shows failed staking, JSON, and IBC precompile paths changing from returning stringified error bytes to returning nil data while still signaling execution failure.

## Search Motifs

- Motif 1: failed precompile returns []byte(err.Error())
- Motif 2: error data bubbles into ABCI result data
- Motif 3: stack path or local diagnostic string appears in consensus-visible bytes

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Signal failure through deterministic error status and return nil or constant data on failed precompile execution.

## False Match Warnings

- Failure data is omitted from committed results.
- The VM error channel signals failure while return data is nil or fixed.
