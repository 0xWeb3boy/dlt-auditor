# Root-Cause Card

## Metadata

- ID: `geth-arb-2015-05-15-go-ethereum-core-logic-cd2fb09051`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `duplicate-hash-replay`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `duplicate-response-deduplication`

## Violated Invariant

- Invariant: Peer-supplied sync batches must contribute new, ordered work or be rejected so duplicate hashes cannot be replayed to waste downloader capacity or bypass progress checks.

## Trust Boundary

- Boundary: untrusted peer hash response -> downloader hash queue

## Attack Surface

- Entrypoint type: peer hash batch handler
- Sensitive sink: sync queue insertion and peer scoring

## Impact Pattern

- Primary impact: sync-availability
- Secondary impact: resource-exhaustion
- Severity guide: medium

## Short Reusable Lesson

- The downloader did not treat a non-final batch of only duplicate hashes as a protocol failure, allowing replayed responses to consume sync work without progress. Count newly inserted hashes and reject non-final responses that add no new queue entries.
