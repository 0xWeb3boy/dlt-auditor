# Validation Card

## Metadata

- ID: `sei-chain-2024-04-15-sei-chain-rpc-client-api-56ce9a974`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `identity-binding-hardening`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says unassociated EOA addresses are disallowed from using precompiles.
- Evidence 2: Affected handlers build ERC20/ERC721 transfer, transferFrom, allowance, and approval-related ABI payloads.

## What Could Have Invalidated It

- Compensating control 1: The payload is informational and cannot be submitted to a state-changing path.
- Compensating control 2: Downstream execution independently rejects unassociated addresses.

## Severity Guidance

- Expected impact band: authorization-or-identity-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The payload is informational and cannot be submitted to a state-changing path.
- Caution 2: Downstream execution independently rejects unassociated addresses.
