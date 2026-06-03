# Root-Cause Card

Record: `omni-cantina-m01-finalizeblock-postfinalize-error-escape`
Project: `omni-network`
Source finding: `Omni Cantina M-1`
Bug family: `state_machine_and_lifecycle_consistency`

## Core Failure

Optional local proposer-prediction work is coupled to the deterministic committed-block application return path.

## Why It Matters

Consensus callbacks are replicated state-machine boundaries. Local RPC availability or snapshot history must not decide whether a committed block applies.

## Reusable Heuristic

Flag consensus lifecycle hooks where local I/O, prediction, cache, telemetry, or prebuild helpers can return fatal errors after deterministic state transition.

## Patch Direction

Treat optimistic build preparation as best effort: log local query failures and never propagate them through FinalizeBlock.
