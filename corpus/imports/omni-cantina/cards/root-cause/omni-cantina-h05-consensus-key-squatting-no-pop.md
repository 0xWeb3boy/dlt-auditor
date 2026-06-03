# Root-Cause Card

Record: `omni-cantina-h05-consensus-key-squatting-no-pop`
Project: `omni-network`
Source finding: `Omni Cantina H-5`
Bug family: `staking_registry_and_accountability`

## Core Failure

Identity reservation is delayed and unauthenticated at the source boundary that accepts value.

## Why It Matters

Public key uniqueness is a scarce registry resource; reserving it without proof enables denial and deposit griefing.

## Reusable Heuristic

For validator, signer, and bridge-key registration, verify possession before key reservation and before accepting funds.

## Patch Direction

Require proof-of-possession over operator, chain, and registration intent; reserve pubkeys at the source boundary or refund failed native delivery.
