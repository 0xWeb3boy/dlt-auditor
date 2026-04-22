# Validation Card

## Metadata

- ID: `base-2026-04-07-base-cryptography-aa3b6d3ca`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- Evidence 1: Commit message states that heavy connection pressure could exhaust memory and task-scheduler resources before handshake timeouts reclaimed them.
- Evidence 2: Listener::run now creates a semaphore from max_connections and requires each accepted connection to acquire a permit before proceeding.

## What Could Have Invalidated It

- Compensating control 1: Supported claim: the patch hardens a network entry point against resource exhaustion from excessive concurrent connections.
- Compensating control 2: Supported claim: the security relevance is availability-focused denial-of-service resistance.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported claim: the patch hardens a network entry point against resource exhaustion from excessive concurrent connections.
- Caution 2: Supported claim: the security relevance is availability-focused denial-of-service resistance.
