---
case_id: case_20220704_362bc47867
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2022-07-04
source_refs:
  - git:362bc478677bf19d8021401ca261c72781ab1bab
  - "crates/sui-core/src/authority_active/gossip/node_sync.rs:375"
  - "crates/sui-core/src/authority_active/gossip/node_sync.rs:341"
  - "crates/sui-core/src/authority_active/checkpoint_driver/mod.rs:551"
  - "crates/sui-core/src/authority_active/gossip/node_sync.rs:51"
bug_class: validator-response-handling
impact_type:
  - availability
  - protocol-liveness
tags:
  - blockchain-core
  - validator
  - checkpoint-sync
  - authority-fetch
  - byzantine-response-hardening
  - availability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Sui authority sync fetching for checkpoints and finalized cert/effects by carrying known authority sets into aggregator fetch APIs. The evidence supports an availability and strict-response hardening claim, not a proven consensus safety break, invalid-certificate acceptance bug, or asset-loss vulnerability.

## Observed Patch Facts

1. In `crates/sui-core/src/authority_active/gossip/node_sync.rs`, the patch replaces `// TODO: should we suggest that we try peer first?` with `let (cert, effects) = aggregator`.

2. In `crates/sui-core/src/authority_active/gossip/node_sync.rs`, the patch replaces `if let Err(error) =` with `let authorities = self.effects_stake.lock().unwrap().voters(&digests.effects);`.

3. In `crates/sui-core/src/authority_active/checkpoint_driver/mod.rs`, the patch replaces `let mut available_authorities = available_authorities.clone();` with `net.get_certified_checkpoint(`.

4. In `crates/sui-core/src/authority_active/gossip/node_sync.rs`, the patch replaces `/// Note that a given effects digest has been attested by a validator, and return tru...` with `// Get the set of authorities who voted for a digest.`.

## Project Context

The changed code sits primarily in `crates/sui-core/src/authority_active/gossip`, `crates/sui-core/src/authority_active`, `crates/sui-core/src/authority_active/checkpoint_driver`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/sui-core/src/authority_active/gossip/mod.rs`, `crates/sui-core/src/authority_active/gossip/tests.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/authority_active/gossip/mod.rs`, `crates/sui-core/src/authority_active/gossip/tests.rs`. The strongest project-level identifiers around this patch are `digest`, `digests`, `Self::download_impl`, and `peer`.

## Before/After Behavior

Before the patch, node sync downloaded cert/effects through an unconstrained transaction/effects info request and handled missing optional response fields locally. The download path was driven by a single peer even though effects votes identify authorities that attested the effects digest. After the patch, node sync derives the voters for the effects digest, passes that authority set into `handle_transaction_and_effects_info_request`, and stores the returned cert/effects pair. Checkpoint fetching changed from local sampling over `available_authorities` to an aggregator call using the known available authority set with no retry limit.

# Root Cause

The fetch paths did not consistently pass the caller's existing knowledge about which authorities should have the requested artifact into the aggregator. That could let absence or unhelpful responses be handled too weakly for known-available checkpoints or cert/effects. The provided evidence does not establish acceptance of invalid data or a direct external exploit path.

## Walkthrough

1. `EffectsStakeMap::voters` was added to recover authorities that voted for a transaction effects digest.

2. `download_cert_and_effects` now derives the authority set from effects voters before spawning the download task.

3. `download_impl` now passes that known authority set into `handle_transaction_and_effects_info_request`.

4. The patched download path stores the returned certified transaction and signed effects pair in `node_sync_store`.

5. `get_one_checkpoint` now delegates to `net.get_certified_checkpoint` with `available_authorities` instead of performing local random sampling.

6. The commit message states the intended strictness: the requester knows which authorities have these structures, so responses claiming absence can be refused.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/authority_active/gossip/node_sync.rs | 51 | Adds EffectsStakeMap::voters so node sync can recover the authorities that attested a transaction effects digest. |
| crates/sui-core/src/authority_active/gossip/node_sync.rs | 326 | Uses the effects voters as the authority set for downloading certified transaction and effects artifacts. |
| crates/sui-core/src/authority_active/gossip/node_sync.rs | 369 | Fetches cert/effects through the aggregator with the known authority set and stores the returned canonical pair. |
| crates/sui-core/src/authority_active/checkpoint_driver/mod.rs | 544 | Fetches a past certified checkpoint through the aggregator using the known available authorities and no retry limit. |
| crates/sui-core/src/authority_aggregator.rs | 0 | Changed aggregator-side request handling for checkpoint and transaction/effects fetches, inferred from commit file list and call-site signature changes. |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/authority_active/gossip/node_sync.rs:375` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
let digest = digests.transaction;

        // TODO: should we suggest that we try peer first?
        let resp = aggregator
            .handle_transaction_and_effects_info_request(digests)
            .await?;

        let cert = resp.certified_transaction.ok_or_else(|| {
```
After
```rust
let digest = digests.transaction;

        let (cert, effects) = aggregator
            .handle_transaction_and_effects_info_request(digests, &authorities, None)
            .await?;

        node_sync_store.store_cert_and_effects(&digest, &(cert, effects))?;
```

## Snippet 2

Context: `crates/sui-core/src/authority_active/gossip/node_sync.rs:341` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
let peer = *peer;
            let node_sync_store = self.node_sync_store.clone();
            tokio::task::spawn(async move {
                if let Err(error) =
                    tx.send(Self::download_impl(peer, aggregator, &digests, node_sync_store).await)
                {
                    error!(?digest, ?peer, ?error, "Could not broadcast cert response");
                }
```
After
```rust
let peer = *peer;
            let node_sync_store = self.node_sync_store.clone();
            let authorities = self.effects_stake.lock().unwrap().voters(&digests.effects);
            tokio::task::spawn(async move {
                if let Err(error) = tx.send(
                    Self::download_impl(authorities, aggregator, &digests, node_sync_store).await,
                ) {
                    error!(?digest, ?peer, ?error, "Could not broadcast cert response");
```

## Snippet 3

Context: `crates/sui-core/src/authority_active/checkpoint_driver/mod.rs:551` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
A: AuthorityAPI + Send + Sync + 'static + Clone,
{
    let mut available_authorities = available_authorities.clone();
    while !available_authorities.is_empty() {
        // Get a random authority by stake
        let sample_authority = net.committee.sample();
        if !available_authorities.contains(sample_authority) {
            // We want to pick an authority that has the checkpoint and its full history.
```
After
```rust
A: AuthorityAPI + Send + Sync + 'static + Clone,
{
    net.get_certified_checkpoint(
        &CheckpointRequest::past(sequence_number, contents),
        available_authorities,
        // Loop forever until we get the cert from someone.
        None,
    )
```

## Snippet 4

Context: `crates/sui-core/src/authority_active/gossip/node_sync.rs:51` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

    /// Note that a given effects digest has been attested by a validator, and return true if the
    /// stake that has attested that effects digest has exceeded the quorum threshold.
```
After
```rust
}

    // Get the set of authorities who voted for a digest.
    pub fn voters(&self, digest: &TransactionEffectsDigest) -> BTreeSet<AuthorityName> {
        self.effects_vote_map
            .get(digest)
            .unwrap_or(&HashMap::new())
            .keys()
```

# Fix Pattern

Thread known authority sets from prior protocol evidence into artifact-fetch APIs, and centralize stricter retry/refusal handling in the aggregator rather than relying on ad hoc caller-side fetch logic.

## How It Was Fixed

The patch adds a helper to retrieve voters for an effects digest, uses those voters as the authority set for cert/effects downloads, changes the aggregator call signature at the call sites to include that authority set and retry limit, and changes checkpoint retrieval to use the aggregator's certified checkpoint fetch over the known available authorities.

# Why It Matters

1. Improves liveness robustness when authorities incorrectly claim not to have data they should have.

2. Avoids treating an unexpected absence response as proof that a checkpoint or cert/effects is unavailable.

3. Keeps strict fetch policy closer to the shared aggregator path.

4. Does not prove invalid certificate acceptance, double spend, or finality compromise.

# Evidence Notes

Grounded evidence comes from `node_sync.rs` excerpts adding `EffectsStakeMap::voters`, passing voters into cert/effects download, and calling `handle_transaction_and_effects_info_request(digests, &authorities, None)`, plus `checkpoint_driver/mod.rs` delegating checkpoint fetch to `get_certified_checkpoint(..., available_authorities, None)`. The commit message supports the strict-response interpretation. Aggregator internals are not shown, so claims about exact quorum failure behavior or exploitability are inferred only from call sites and commit text. Protocol security invariant: When the requester already has protocol evidence that specific authorities should possess a certified checkpoint or finalized cert/effects, fetch logic should query that known authority set and treat an unexpected absence response as a failed authority response rather than as authoritative evidence that the artifact is unavailable. Verification notes: The patch does not prove that invalid certificates or effects could be accepted. The patch does not prove transaction safety, double-spend, or consensus finality compromise. The patch does not show an external attacker path beyond faulty or unhelpful authority responses. The patch evidence supports availability and strict-response hardening more strongly than confidentiality or integrity exploitation. The exact authority_aggregator.rs line-level behavior is not shown in the provided excerpts. Line-level evidence for `authority_aggregator.rs` was not provided. No evidence proves invalid artifacts could be accepted before the patch. No evidence proves a direct external attacker path. Security classification is hardening-oriented and should remain medium confidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `validator-response-handling`
Final impact type: `availability, protocol-liveness`
Final tags: `blockchain-core, validator, checkpoint-sync, authority-fetch, byzantine-response-hardening, availability`

The provided patch evidence supports a conservative security-hardening classification: it threads known authority sets into checkpoint and cert/effects fetch paths so authorities known to possess data can be treated more strictly when claiming absence. This is security-relevant in a validator/consensus-adjacent subsystem, but the evidence does not prove invalid data acceptance, signature bypass, asset loss, or a concrete exploitable vulnerability. The original serialization/state-representation and client-view-divergence framing is too specific for the shown patch.

## Security Evidence

1. Commit message explicitly says requesters know which authorities have checkpoints and certs/effects and can refuse absence claims strictly.
2. Cert/effects download now derives voters for the effects digest and passes that authority set into the aggregator fetch API.
3. Checkpoint fetching now delegates to an aggregator call using the known available authorities with no retry limit.
4. Changed code is in validator gossip, checkpoint, and authority aggregation paths.

## Missing Evidence

1. No aggregator internals are shown to prove exact refusal or quorum behavior.
2. No evidence shows invalid certificates or effects could previously be accepted.
3. No evidence shows a direct external attacker path or asset-impacting exploit.
4. No evidence proves client-view divergence or state representation corruption.

## Claim Boundaries

1. Keep the finding as hardening, not a proven vulnerability fix.
2. Limit impact claims to availability and protocol liveness under faulty or unhelpful authority responses.
3. Do not claim signature validation, double-spend prevention, finality safety, or confidentiality impact.
4. Do not retain the original serialization-or-state-representation bug class.
