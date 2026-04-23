# Root-Cause Card

## Metadata

- ID: `nitro-2022-09-07-nitro-transaction-processing-4f32fd7c7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `message-integrity-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `contiguous-sequence-enforcement`

## Violated Invariant

- Invariant: Broadcast-feed messages should preserve contiguous sequence numbers on ingest and receive uniform signing behavior on emission.

## Trust Boundary

- Boundary: `broadcast-feed input->stream ingestion and emission`

## Attack Surface

- Entrypoint type: `protocol-stream-ingestion`
- Sensitive sink: `accepting or forwarding ordered feed messages`

## Impact Pattern

- Primary impact: `protocol-integrity-risk`
- Secondary impact: `none`

## Short Reusable Lesson

- Broadcast-feed messages should preserve contiguous sequence numbers on ingest and receive uniform signing behavior on emission. The strongest supported reading is protocol-integrity hardening in the broadcast-feed path, not a confirmed vulnerability fix. The patch adds explicit contiguous-sequence checks during broadcast ingestion and removes a `RequestId` condition so outbound messages are signed whenever a signer exists. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
