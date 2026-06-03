# Root-Cause Card

Record: `omni-cantina-m04-empty-transaction-proposal-bloat`
Project: `omni-network`
Source finding: `Omni Cantina M-4`
Bug family: `resource_accounting_and_limits`

## Core Failure

The router checks message cardinality but forgets transaction cardinality, allowing useless data to consume validation and storage resources.

## Why It Matters

Bounds must apply at the outer container as well as the inner semantic message list.

## Reusable Heuristic

For generated consensus transactions, verify ProcessProposal enforces the exact expected outer shape, not just allowed inner messages.

## Patch Direction

Enforce the protocol expectation of one generated transaction per proposal, or set explicit max transaction count/byte limits and reject empty-message transactions.
