# Validation Card

## Metadata

- ID: `base-2025-10-14-base-rpc-client-api-f694185fe`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-state-validation`

## What Confirmed The Issue

- Evidence 1: The proposer logic changes from direct reuse of an existing checkpoint to conditional reuse only when it still matches the on-chain mapping.
- Evidence 2: A new contract interface getter, `historicBlockHashes(uint256)`, is added specifically to support validation against canonical on-chain state.

## What Could Have Invalidated It

- Compensating control 1: Supported claim: cached checkpoint reuse is now guarded by validation against contract state before reuse.
- Compensating control 2: Supported claim: this is security-relevant hardening for integrity-sensitive blockchain logic.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported claim: cached checkpoint reuse is now guarded by validation against contract state before reuse.
- Caution 2: Supported claim: this is security-relevant hardening for integrity-sensitive blockchain logic.
