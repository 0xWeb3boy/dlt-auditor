# Code-Shape Card

## Metadata

- ID: `bor-2026-03-05-bor-consensus-26dc364ff`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## Code Shape Summary

- The patch clearly fixes out-of-range block-number handling in Bor milestone lock/sync logic, but the provided evidence does not establish a concrete security vulnerability or attacker-controlled trigger. The strongest supported claim is robustness hardening around overflow-prone arithmetic and corrupted persisted lock state. Root cause: Missing range validation for block-height values and trust in persisted lock metadata that could be outside the safe block-number range used by later logic.

## Search Motifs

- gas, fee, size, or work accounting uses unchecked add/mul/cast on attacker-influenced values
- large protocol parameter crosses uint/int or narrow/wide type boundary before validation
- resource charge is computed after state mutation or uses a value that can wrap or truncate

## Typical Asymmetry

- Attacker-controlled data crosses external RPC client to node service boundary and reaches backend state access, privileged API behavior, or response serialization before the missing property is enforced.

## Patch Pattern

- Add explicit upper-bound validation before block-number arithmetic and sanitize persisted state that falls outside the accepted numeric domain.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
