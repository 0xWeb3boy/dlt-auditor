# Root-Cause Card

Record: `omni-cantina-h06-same-block-staking-event-order-loss`
Project: `omni-network`
Source finding: `Omni Cantina H-6`
Bug family: `state_machine_and_lifecycle_consistency`

## Core Failure

The EVM-to-native event adapter erases source ordering for dependent state transitions.

## Why It Matters

Event order is part of the semantics for generated work; sorting for determinism must not destroy dependency order.

## Reusable Heuristic

Whenever logs are reduced or sorted before cross-runtime execution, search for dependent event pairs and skipped-error semantics.

## Patch Direction

Include source log index in event ordering or preserve original log order; make failed mandatory staking delivery retryable/fail-closed.
