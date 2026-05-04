---
case_id: case_20201118_5ee41881b9
project: stacks-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: rpc-client-api
confidence: medium
source_quality: high
date: 2020-11-18
source_refs:
  - git:5ee41881b94277859e39ac413ca14290328aead4
  - "src/net/rpc.rs:562"
  - "src/net/atlas/download.rs:930"
  - "src/net/rpc.rs:2258"
  - "src/net/atlas/download.rs:219"
bug_class: unbounded-request-size
impact_type:
  - availability
tags:
  - blockchain-core
  - rpc
  - atlas
  - resource-control
  - request-size-limit
  - availability-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a request-size bound to the Atlas attachment inventory RPC flow. The supported claim is availability/resource-control hardening for an externally reachable request shape, not state corruption, consensus failure, authorization bypass, or a proven denial-of-service exploit.

## Observed Patch Facts

1. In `src/net/rpc.rs`, the patch replaces `let mut pages_indexes = pages_indexes.iter().map(|i| *i).collect::<Vec<u32>>();` with `if pages_indexes.len() > MAX_ATTACHMENT_INV_PAGES_PER_REQUEST {`.

2. In `src/net/atlas/download.rs`, the patch replaces `pub fn resolve_attachment(&mut self, content_hash: &Hash160) {` with `pub fn get_paginated_missing_pages_for_contract_id(`.

3. In `src/net/rpc.rs`, the patch adds `/// Make a new request for attachment inventory page`.

4. In `src/net/atlas/download.rs`, the patch replaces `pages: self` with `for pages in self.attachments_batch.get_paginated_missing_pages_for_contract_id(contr...`.

## Project Context

The changed code sits primarily in `src/net`, `src/net/atlas`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `src/net/atlas/tests.rs`, `src/net/atlas/onchain.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/net/atlas/tests.rs`, `src/net/atlas/onchain.rs`. The strongest project-level identifiers around this patch are `contract_id`, `clone`, `pages_indexes`, and `attachments_batch`.

## Before/After Behavior

Before the patch, the inbound GetAttachmentsInv handler converted and sorted the supplied page-index set with no maximum-count check shown in the evidence, and the downloader could enqueue one inventory request containing all missing pages for a contract. After the patch, the handler rejects requests whose page-index count exceeds MAX_ATTACHMENT_INV_PAGES_PER_REQUEST, and the downloader chunks missing page indexes into bounded requests.

# Root Cause

The GetAttachmentsInv request path lacked an enforced maximum number of requested attachment inventory pages per request. The local downloader also constructed requests without applying that bound.

## Walkthrough

1. A peer can submit a GetAttachmentsInv request with a set of attachment inventory page indexes.

2. The pre-patch handler evidence shows the supplied set being converted and sorted without a visible maximum-count guard.

3. The pre-patch downloader evidence shows all missing pages for a contract being placed into one AttachmentsInventoryRequest.

4. The patch adds a server-side length check against MAX_ATTACHMENT_INV_PAGES_PER_REQUEST in handle_getattachmentsinv.

5. Oversized inbound requests receive a ServerError response and are not processed further in that handler.

6. The downloader now paginates missing page indexes into chunks capped by MAX_ATTACHMENT_INV_PAGES_PER_REQUEST before queueing requests.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/net/rpc.rs | 551 | Inbound GetAttachmentsInv HTTP handler now rejects requests whose page-index set exceeds MAX_ATTACHMENT_INV_PAGES_PER_REQUEST. |
| src/net/atlas/download.rs | 215 | Atlas attachment inventory request queue now emits one request per bounded chunk of missing pages. |
| src/net/atlas/download.rs | 919 | AttachmentsBatch helper computes missing pages and paginates them into MAX_ATTACHMENT_INV_PAGES_PER_REQUEST-sized vectors. |
| src/net/rpc.rs | 2241 | HTTP request construction path for GetAttachmentsInv accepts the bounded page-index set used by the downloader. |

## Code Snippets

## Snippet 1

Context: `src/net/rpc.rs:562` (changes a sensitive control or state-update path)

Before
```rust
) -> Result<(), net_error> {
        let response_metadata = HttpResponseMetadata::from(req);
        let mut pages_indexes = pages_indexes.iter().map(|i| *i).collect::<Vec<u32>>();
        pages_indexes.sort();
```
After
```rust
) -> Result<(), net_error> {
        let response_metadata = HttpResponseMetadata::from(req);
        if pages_indexes.len() > MAX_ATTACHMENT_INV_PAGES_PER_REQUEST {
            let msg = format!("Number of attachment inv pages is limited by {} per request", MAX_ATTACHMENT_INV_PAGES_PER_REQUEST);
            warn!("{}", msg);
            let response = HttpResponseType::ServerError(response_metadata, msg.clone());
            response.send(http, fd)?;
            return Ok(())
```

## Snippet 2

Context: `src/net/atlas/download.rs:930` (changes a sensitive control or state-update path)

Before
```rust
}

    pub fn resolve_attachment(&mut self, content_hash: &Hash160) {
        for missing_attachments in self.attachments_instances.values_mut() {
```
After
```rust
}

    pub fn get_paginated_missing_pages_for_contract_id(
        &self,
        contract_id: &QualifiedContractIdentifier,
    ) -> Vec<Vec<u32>> {
        let mut paginated = vec![];
        let pages_indexes = self.get_missing_pages_for_contract_id(contract_id);
```

## Snippet 3

Context: `src/net/rpc.rs:2258` (changes a sensitive control or state-update path)

Before
```rust
)
    }
}
```
After
```rust
)
    }

    /// Make a new request for attachment inventory page
    pub fn new_getattachmentsinv(
        &self,
        tip_opt: Option<StacksBlockId>,
        pages_indexes: HashSet<u32>,
```

## Snippet 4

Context: `src/net/atlas/download.rs:219` (changes bounds, limits, or capacity handling)

Before
```rust
for (contract_id, _) in self.attachments_batch.attachments_instances.iter() {
            for (peer_url, reliability_report) in self.peers.iter() {
                let request = AttachmentsInventoryRequest {
                    url: peer_url.clone(),
                    reliability_report: reliability_report.clone(),
                    contract_id: contract_id.clone(),
                    pages: self
                        .attachments_batch
```
After
```rust
for (contract_id, _) in self.attachments_batch.attachments_instances.iter() {
            for (peer_url, reliability_report) in self.peers.iter() {
                for pages in self.attachments_batch.get_paginated_missing_pages_for_contract_id(contract_id) {
                    let request = AttachmentsInventoryRequest {
                        url: peer_url.clone(),
                        reliability_report: reliability_report.clone(),
                        contract_id: contract_id.clone(),
                        pages: pages,
```

# Fix Pattern

Enforce a protocol-level resource bound at the inbound RPC boundary and make the local request producer generate only compliant bounded batches.

## How It Was Fixed

src/net/rpc.rs adds a pages_indexes.len() check in handle_getattachmentsinv and returns a ServerError when the request exceeds MAX_ATTACHMENT_INV_PAGES_PER_REQUEST. src/net/atlas/download.rs adds get_paginated_missing_pages_for_contract_id and updates request queueing to emit one AttachmentsInventoryRequest per bounded chunk.

# Why It Matters

1. Bounds an externally visible Atlas inventory RPC input.

2. Prevents one request from carrying an arbitrary number of page indexes.

3. Aligns local downloader behavior with the server-side request limit.

4. Supports availability hardening, but exploitability is not proven by the supplied evidence.

# Evidence Notes

The strongest evidence is the explicit MAX_ATTACHMENT_INV_PAGES_PER_REQUEST guard in src/net/rpc.rs and the matching pagination logic in src/net/atlas/download.rs. The evidence does not quantify CPU, memory, bandwidth, or database impact, so a practical denial-of-service claim is not confirmed. The state-corruption and consensus-related labels from the heuristic baseline are unsupported. Protocol security invariant: Atlas GetAttachmentsInv requests should contain no more than MAX_ATTACHMENT_INV_PAGES_PER_REQUEST page indexes, and local request generation should split larger missing-page sets into bounded batches. Verification notes: The patch does not prove a practical remote denial-of-service exploit by itself. The patch does not show consensus validation or chain state corruption being fixed. The evidence does not quantify CPU, memory, bandwidth, or database impact from oversized requests. No authentication, authorization, or data-confidentiality failure is shown. The heuristic baseline's state-corruption label is not supported by the provided patch evidence. No test output was provided in the input. No exploit proof or resource-impact measurement was provided. The classification is based only on the supplied diff excerpts and commit subject. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unbounded-request-size`
Final impact type: `availability`
Final tags: `blockchain-core, rpc, atlas, resource-control, request-size-limit, availability-hardening`

The supplied patch evidence supports retaining this as security hardening: it adds an explicit maximum count for externally supplied GetAttachmentsInv page indexes and updates the local downloader to emit bounded request chunks. The evidence does not support the original state-corruption or consensus-integrity framing, and it does not prove a concrete exploitable denial-of-service bug, but it clearly tightens resource-control behavior on a network/RPC path.

## Security Evidence

1. Inbound GetAttachmentsInv handling now rejects requests where pages_indexes.len() exceeds MAX_ATTACHMENT_INV_PAGES_PER_REQUEST.
2. Oversized inbound requests receive a ServerError response and return before further processing in the shown handler path.
3. Downloader request generation now chunks missing page indexes using the same MAX_ATTACHMENT_INV_PAGES_PER_REQUEST bound.
4. The commit subject explicitly describes adding a limit on attachment inventory pages a node can ask for.

## Missing Evidence

1. No measured CPU, memory, bandwidth, database, or queue impact from oversized requests is provided.
2. No exploit scenario or proof of practical denial of service is shown.
3. No evidence shows state corruption, consensus failure, authorization bypass, or confidentiality impact.
4. No tests or runtime verification output are included in the supplied input.

## Claim Boundaries

1. Valid claim is resource-control and availability hardening for an RPC request shape.
2. Do not classify this as state corruption or consensus integrity without additional evidence.
3. Do not claim a confirmed denial-of-service vulnerability from this patch alone.
4. Do not infer authentication, authorization, or data confidentiality impact.
