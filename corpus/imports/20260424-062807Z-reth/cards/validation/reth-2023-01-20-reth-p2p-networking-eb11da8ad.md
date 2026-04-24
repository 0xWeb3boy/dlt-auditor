# Validation Card

## Metadata

- ID: `reth-2023-01-20-reth-p2p-networking-eb11da8ad`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-handshake-state-inconsistency`

## What Confirmed The Issue

- ForkFilter is described as being used for authenticating sessions.
- The build path now derives both status and fork_filter from the same resolved ChainSpec and head.

## What Could Have Invalidated It

- No proof that the old code accepted malicious or wrong-chain peers in practice
- No test, advisory, or commit message explicitly describing a vulnerability or attack scenario

## Severity Guidance

- Expected impact band: auth_or_access_control
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that the old code accepted malicious or wrong-chain peers in practice
- No test, advisory, or commit message explicitly describing a vulnerability or attack scenario
