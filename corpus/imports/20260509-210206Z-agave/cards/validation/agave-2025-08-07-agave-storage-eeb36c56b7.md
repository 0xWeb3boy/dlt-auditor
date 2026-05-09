# Validation Card

## Metadata

- ID: `agave-2025-08-07-agave-storage-eeb36c56b7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-hardening`

## What Confirmed The Issue

- Buffer sizing now uses min(input_archive_size, actual_limit_size) capped by MAX_UNPACK_WRITE_BUF_SIZE.
- The old forced MIN_UNPACK_WRITE_BUF_SIZE is removed and archive metadata length is passed into unpacking.

## What Could Have Invalidated It

- Attackers cannot influence any archive unpacked by the node.
- The old minimum allocation is too small to matter and all archives are already size-gated elsewhere.

## Severity Guidance

- Expected impact band: `resource hardening`
- Expected severity band: `low`
- Rationale: The change reduces unnecessary memory/backlog exposure, but no exploit path, crash, OOM, or attacker-controlled distribution channel was proven.

## False-Positive Cautions

- Performance-oriented buffer tuning should not be treated as security without an untrusted archive source or resource impact.
- Do not infer decompression bomb exposure unless expansion limits are missing too.
