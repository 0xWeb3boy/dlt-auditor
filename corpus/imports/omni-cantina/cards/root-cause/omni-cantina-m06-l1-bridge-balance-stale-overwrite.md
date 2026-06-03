# Root-Cause Card

Record: `omni-cantina-m06-l1-bridge-balance-stale-overwrite`
Project: `omni-network`
Source finding: `Omni Cantina M-6`
Bug family: `state_machine_and_lifecycle_consistency`

## Core Failure

An asynchronous mirror uses stale absolute snapshots across independently timed bridge directions.

## Why It Matters

Bridge authentication does not imply reserve freshness. Settlement admission must reflect current or causally ordered liquidity.

## Reusable Heuristic

For mirrored reserves, inspect whether delayed absolute snapshots can race with local deltas and whether failed settlement refunds source value.

## Patch Direction

Use delta or causally ordered reserve accounting, reject stale snapshots, track pending withdrawals, and refund source funds on failed destination settlement.
