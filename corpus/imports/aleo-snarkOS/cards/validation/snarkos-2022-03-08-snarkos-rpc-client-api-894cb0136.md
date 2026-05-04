# Validation Card

## Metadata

- ID: `snarkos-2022-03-08-snarkos-rpc-client-api-894cb0136`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `network-message-framing-hardening`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Read minimal frame metadata first, enforce bounded expected-message sizes, skip unnecessary deserialization, and drain discarded payloads.
- Root-cause evidence from the finding: The supported root cause is defensive parsing/stream-handling weakness in crawler message ingestion: unwanted framed messages were classified early, and the evidence does not show their remaining payload bytes being consumed before the patch. The evidence does not support claims of RPC state inconsistency, cryptographic failure, consensus impact, authentication bypass, memory corruption, or a proven production-node denial of service. 1. A peer sends a length-prefixed message to the crawler. 2. T

## What Could Have Invalidated It

- Transport codec enforces frame length and drains bodies.
- Affected node is not production consensus infrastructure.

## Severity Guidance

- Expected impact band: `parser-hardening`
- Expected severity band: `low`
- Rationale: Low severity is appropriate when the affected boundary is reachable and the sink controls stream desynchronization or wasted deserialization; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- Crawler-only code has lower chain-security impact
- If each frame is on a fresh connection, stream alignment is irrelevant
- A lower codec layer may already drain rejected frames
