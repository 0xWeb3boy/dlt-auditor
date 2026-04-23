# Validation Card

## Metadata

- ID: `reth-2025-05-28-reth-storage-1cfe50998`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`

## What Confirmed The Issue

- Evidence 1: The patch adds or restores a fail-closed check, state update, or accounting reconstruction in a security-sensitive path.
- Evidence 2: The changed path sits on a trust boundary: Forked in-memory block ancestry crossing into canonical persistence and database handoff.

## What Could Have Invalidated It

- Compensating control 1: Another mandatory validation layer already enforces the same invariant before this code can affect security-sensitive state.
- Compensating control 2: The changed branch is reachable only from trusted tests, offline tooling, or non-production maintenance flows.

## Severity Guidance

- Expected impact band: state_integrity_hardening
- Expected severity band: medium

## False-Positive Cautions

- Missing derived data may only occur in rare internal reorg states.
- A guarded skip is not proof of database corruption.
- Need evidence of persisted bad state before calling this a confirmed vulnerability.
