# Code-Shape Card

## Metadata

- ID: `stacks-core-2020-11-18-stacks-core-rpc-client-api-5ee41881b9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-request-size`

## Code Shape Summary

- The patch adds a request-size bound to the Atlas attachment inventory RPC flow. The supported claim is availability/resource-control hardening for an externally reachable request shape, not state corruption, consensus failure, authorization bypass, or a proven denial-of-service exploit. Structural cue: In `src/net/rpc.rs`, the patch replaces `let mut pages_indexes = pages_indexes.iter().map(|i| In `src/net/atlas/download.rs`, the patch replaces `pub fn resolve_attachment(&mut self, content_hash: &Hash160) {`

## Search Motifs

- Motif 1: request body decoded before max-size enforcement
- Motif 2: panic or unwrap reachable from peer-controlled protocol data
- Motif 3: execution cost or resource budget charged inconsistently across error cases

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Move size, cost, and error checks to the boundary and convert panic or ambiguous errors into explicit validation failures.

## False Match Warnings

- The input may already be bounded by transport framing.
- A panic in test-only or unreachable internal code is not an externally reachable denial of service.
