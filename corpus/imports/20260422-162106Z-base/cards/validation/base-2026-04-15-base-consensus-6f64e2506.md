# Validation Card

## Metadata

- ID: `base-2026-04-15-base-consensus-6f64e2506`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- Evidence 1: The RPC server middleware adds `ConcurrencyLimitLayer` to bound in-flight requests.
- Evidence 2: The RPC server middleware adds `LoadShedLayer` to reject excess requests instead of queueing them indefinitely.

## What Could Have Invalidated It

- Compensating control 1: Supported: the commit hardens the RPC ingress against overload/flood conditions.
- Compensating control 2: Supported: the change mitigates resource-exhaustion risk at an externally reachable service boundary.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported: the commit hardens the RPC ingress against overload/flood conditions.
- Caution 2: Supported: the change mitigates resource-exhaustion risk at an externally reachable service boundary.
