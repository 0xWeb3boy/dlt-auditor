# Code-Shape Card

## Metadata

- ID: `base-2026-04-15-base-consensus-6f64e2506`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- Short description of what the buggy code looked like: Missing admission control at the RPC ingress. In the provided pre-patch code, requests were subject to a timeout but not to an explicit concurrency bound or immediate overload rejection path, leaving the service more exposed to backlog growth under bursty or flood-like request pressure.

## Search Motifs

- Motif 1: unbounded task spawning on a network-facing listener or RPC ingress
- Motif 2: no semaphore, queue bound, or backpressure before expensive async work
- Motif 3: timeouts or retries present without an explicit concurrency cap

## Typical Asymmetry

- What was checked in one path but missing in another: The code had timeout or retry behavior, but did not put a hard bound on how much concurrent external work could enter the expensive path.

## Patch Pattern

- What the fix changed structurally: Add ingress admission control to a request-handling boundary: enforce a bounded concurrency limit, shed excess load instead of allowing unbounded backlog, and place timeout accounting so it covers time spent waiting for capacity.

## False Match Warnings

- What looks similar but is often not a bug: Supported: the commit hardens the RPC ingress against overload/flood conditions.
