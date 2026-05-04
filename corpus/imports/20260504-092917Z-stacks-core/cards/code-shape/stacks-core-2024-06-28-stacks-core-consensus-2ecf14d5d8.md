# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-06-28-stacks-core-consensus-2ecf14d5d8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-tip-monotonicity`

## Code Shape Summary

- The patch changes Nakamoto canonical tip handling in the sortition DB so an accepted block only advances the memoized canonical tip when it is higher than the current tip for the same sortition history. This is plausibly important consensus state maintenance, but the provided evidence does not establish an exploitable vulnerability or concrete security impact.

## Search Motifs

- Motif 1: lookup by height without fork id or canonical tip
- Motif 2: equivocation evidence requires overly narrow matching fields
- Motif 3: reward set or signer set loaded without canonical context

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Thread canonical chain context into validation and reject evidence or lookups that do not match the active fork/tip rules.

## False Match Warnings

- The value may be used only for display or diagnostics.
- Another validation layer may enforce canonical context before finalization.
