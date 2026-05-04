# Root-Cause Card

## Metadata

- ID: `stacks-core-2020-11-18-stacks-core-rpc-client-api-5ee41881b9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-request-size`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-bounds-and-error-containment`

## Violated Invariant

- Invariant: Untrusted inputs and execution paths must be bounded and must fail closed without panics, unmetered work, or inconsistent accounting.

## Trust Boundary

- Boundary: External RPC client request crosses into node parsing, allocation, and response construction.

## Attack Surface

- Entrypoint type: `rpc_http_request`
- Sensitive sink: request decoder, allocation path, or RPC response generator

## Impact Pattern

- Primary impact: availability
- Secondary impact: denial-of-service

## Short Reusable Lesson

- The patch adds a request-size bound to the Atlas attachment inventory RPC flow. The supported claim is availability/resource-control hardening for an externally reachable request shape, not state corruption, consensus failure, authorization bypass, or a proven denial-of-service exploit. Structural cue: In `src/net/rpc.rs`, the patch replaces `let mut pages_indexes = pages_indexes.iter().map(|i| In `src/net/atlas/download.rs`, the patch replaces `pub fn resolve_attachment(&mut self, content_hash: &Hash160) {`
