# Root-Cause Card

Record: `omni-cantina-h01-blob-payload-versioned-hashes-omitted`
Project: `omni-network`
Source finding: `Omni Cantina H-1`
Bug family: `input_validation_and_invariant_enforcement`

## Core Failure

The consensus representation is not equivalent to the execution-client representation for Cancun payloads.

## Why It Matters

Safety checks in the execution client turn into an availability failure when the application drops required fork side data.

## Reusable Heuristic

For every execution fork, compare what the proposer receives from the engine, what consensus commits, and what validators replay into the engine.

## Patch Direction

Reject blob transactions/payloads until supported, or derive and pass the payload transaction BlobHashes to NewPayloadV3; commit blob availability data if needed.
