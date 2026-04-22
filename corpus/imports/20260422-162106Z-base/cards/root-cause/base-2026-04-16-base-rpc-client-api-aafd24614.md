# Root-Cause Card

## Metadata

- ID: `base-2026-04-16-base-rpc-client-api-aafd24614`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `audit-log-integrity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `append-only-history`

## Violated Invariant

- Invariant: Audit history storage should preserve each bundle event exactly once and reconstruct complete history without losing prior events when writes are retried or occur concurrently.

## Trust Boundary

- Boundary: `audit event producer->append-only object storage`

## Attack Surface

- Entrypoint type: `audit-event-persistence`
- Sensitive sink: `append-only audit history and operator-visible forensic records`

## Impact Pattern

- Primary impact: `integrity-loss`
- Secondary impact: `event-loss`

## Short Reusable Lesson

- Audit history storage should preserve each bundle event exactly once and reconstruct complete history without losing prior events when writes are retried or occur concurrently. The evidence suggests the old design used read-modify-write updates against one shared bundle-history object in S3, which the new comments describe as creating read-modify-write contention. The patch addresses that by making each event an immutable record with write-once semantics, but the excerpts do not prove a specific pre-patch failure beyond that contention risk. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
