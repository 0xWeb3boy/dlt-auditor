# Code-Shape Card

## Metadata

- ID: `base-2026-04-07-base-cryptography-aa3b6d3ca`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- Short description of what the buggy code looked like: Missing admission control in the listener accept loop allowed connection pressure to create too many concurrent handshake and broadcast tasks before existing timeout mechanisms reclaimed resources.

## Search Motifs

- Motif 1: unbounded task spawning on a network-facing listener or RPC ingress
- Motif 2: no semaphore, queue bound, or backpressure before expensive async work
- Motif 3: timeouts or retries present without an explicit concurrency cap

## Typical Asymmetry

- What was checked in one path but missing in another: The code had timeout or retry behavior, but did not put a hard bound on how much concurrent external work could enter the expensive path.

## Patch Pattern

- What the fix changed structurally: Add an early resource-admission check at the network entry point, backed by a bounded-concurrency primitive and explicit rejection telemetry.

## False Match Warnings

- What looks similar but is often not a bug: Supported claim: the patch hardens a network entry point against resource exhaustion from excessive concurrent connections.
