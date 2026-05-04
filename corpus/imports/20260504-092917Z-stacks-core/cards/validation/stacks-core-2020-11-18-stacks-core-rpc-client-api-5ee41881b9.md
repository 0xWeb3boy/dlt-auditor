# Validation Card

## Metadata

- ID: `stacks-core-2020-11-18-stacks-core-rpc-client-api-5ee41881b9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-request-size`

## What Confirmed The Issue

- Evidence 1: In `src/net/rpc.rs`, the patch replaces `let mut pages_indexes = pages_indexes.iter().map(|i| *i).collect::<Vec<u32>>();` with `if pages_indexes.len() > MAX_ATTACHMENT_INV_PAGES_PER_REQUEST {`.
- Evidence 2: In `src/net/atlas/download.rs`, the patch replaces `pub fn resolve_attachment(&mut self, content_hash: &Hash160) {` with `pub fn get_paginated_missing_pages_for_contract_id(`.

## What Could Have Invalidated It

- Compensating control 1: The input may already be bounded by transport framing.
- Compensating control 2: A panic in test-only or unreachable internal code is not an externally reachable denial of service.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: The input may already be bounded by transport framing.
- Caution 2: A panic in test-only or unreachable internal code is not an externally reachable denial of service.
