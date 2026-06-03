# Root-Cause Card

Record: `omni-cantina-m02-aggvotes-expensive-before-bounds`
Project: `omni-network`
Source finding: `Omni Cantina M-2`
Bug family: `resource_accounting_and_limits`

## Core Failure

The validation pipeline spends expensive cryptographic resources before enforcing cheap structural and membership constraints.

## Why It Matters

Consensus proposal validation is on the critical path for every validator, so wasted work can become liveness loss.

## Reusable Heuristic

Look for proposal, block, or gossip validation where proof verification, signature recovery, decompression, hashing, or JSON decode precedes cheap local bounds.

## Patch Direction

Move count, chain, window, duplicate, and claimed-membership checks ahead of signature recovery; enforce explicit local byte/count limits.
