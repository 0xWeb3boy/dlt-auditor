# Validation Card

## Metadata

- ID: `base-2025-12-29-base-storage-55893ad15`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-runtime-policy-check`

## What Confirmed The Issue

- Evidence 1: Adds an early-return guard before game creation when `self.config.game_type != respected_game_type`.
- Evidence 2: Reads the authoritative onchain policy from `AnchorStateRegistry.respectedGameType()` rather than relying only on local config.

## What Could Have Invalidated It

- Compensating control 1: The evidence supports a missing proposer-side policy validation guard, not `state-corruption` or a storage bug.
- Compensating control 2: The patch shows hardening against stale or incorrect configuration, not a proven exploitable vulnerability.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: The evidence supports a missing proposer-side policy validation guard, not `state-corruption` or a storage bug.
- Caution 2: The patch shows hardening against stale or incorrect configuration, not a proven exploitable vulnerability.
