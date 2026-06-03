# Root-Cause Card

Record: `omni-cantina-h03-engine-api-json-rpc-retry-forever`
Project: `omni-network`
Source finding: `Omni Cantina H-3`
Bug family: `state_machine_and_lifecycle_consistency`

## Core Failure

Transient transport recovery and deterministic payload rejection share the same unbounded retry path.

## Why It Matters

Consensus validation must converge. A proposer-controlled deterministic error cannot be retried forever without halting the round.

## Reusable Heuristic

Inspect retry loops around external clients in consensus validation and classify whether attacker-controlled invalid input can produce an error indistinguishable from network failure.

## Patch Direction

Classify Engine API errors by type: retry only transient transport/sync failures, reject deterministic invalid payload or invalid-parameter errors, and locally validate required fork fields.
