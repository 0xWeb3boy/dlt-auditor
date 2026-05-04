---
case_id: case_20191118_73eb572ac2
project: stacks-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2019-11-18
source_refs:
  - git:73eb572ac2c2656065acd16d1272d75e96afd6df
  - "src/chainstate/stacks/db/blocks.rs:928"
  - "src/net/mod.rs:1010"
  - "src/burnchains/burnchain.rs:1370"
  - "src/chainstate/stacks/transaction.rs:246"
bug_class: protocol-equivocation-detection-gap
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - protocol
  - consensus
  - microblocks
  - equivocation
  - validation
  - poison-evidence
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a protocol-level microblock equivocation detection fix. The patch broadens conflict handling so signed microblocks that share a parent are treated as conflicting, and PoisonMicroblock deserialization accepts evidence when headers share either sequence number or parent block hash.

## Observed Patch Facts

1. In `src/chainstate/stacks/db/blocks.rs`, the patch replaces `// hashes are contiguous enough -- for each seqnum, there is a block with seqnum+1 wi...` with `// sanity check -- all parent block hashes are unique. If there are duplicates, then the`.

2. In `src/net/mod.rs`, the patch replaces `let mut burndb = self.burndb.take().unwrap();` with `let burndb = self.burndb.take().unwrap();`.

3. In `src/burnchains/burnchain.rs`, the patch replaces `let mut expected_winning_hashes = vec![` with `let expected_winning_hashes = vec![`.

4. In `src/chainstate/stacks/transaction.rs`, the patch replaces `// must have the same sequence number and block parent` with `// must have the same sequence number or same block parent`.

## Project Context

The changed code sits primarily in `src/chainstate/stacks/db`, `src/chainstate/stacks`, `src/net`, which anchors the finding in the `storage` area of the project. Historical context from `src/chainstate/stacks/block.rs`, `src/chainstate/stacks/miner.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/chainstate/stacks/miner.rs`, `src/chainstate/stacks/db/mod.rs`. The strongest project-level identifiers around this patch are `prev_block`, `block`, `sequence`, and `burndb`.

## Before/After Behavior

Before the patch, PoisonMicroblock deserialization required two headers to share both sequence and parent, and the provided stream-validation hunk did not show duplicate-parent detection. After the patch, stream validation detects duplicate prev_block values among signed microblocks and returns a PoisonMicroblock payload, while deserialization accepts two distinct headers that share either sequence or prev_block.

# Root Cause

The conflict predicate for microblock equivocation was narrower than the invariant stated by the commit and code comments. One valid conflict shape, distinct signed microblocks with the same parent block hash, was not consistently detected and accepted as PoisonMicroblock evidence.

## Walkthrough

1. The validator filters microblocks to those signed by the expected microblock key.

2. It checks the stream starts at sequence 0 and connects to the parent anchored block.

3. The patch adds a HashMap keyed by signed_microblock.header.prev_block.

4. If another signed microblock uses a previously seen prev_block, the validator treats it as a deliberate fork and returns a PoisonMicroblock payload with both headers.

5. The PoisonMicroblock deserializer still rejects identical headers.

6. The deserializer now rejects only when both sequence and prev_block differ, allowing evidence based on either shared sequence or shared parent.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/chainstate/stacks/db/blocks.rs | 928 | Validates signed parent microblock streams and now treats duplicate prev_block values as deliberate microblock forks, returning a PoisonMicroblock payload. |
| src/chainstate/stacks/transaction.rs | 246 | Deserializes PoisonMicroblock transaction payloads and now accepts conflicting headers that share either sequence number or parent block hash. |
| src/net/mod.rs | 1010 | Test helper warning cleanup; no security-relevant behavior shown. |
| src/burnchains/burnchain.rs | 1370 | Unit-test expected value mutability cleanup; no security-relevant behavior shown. |

## Code Snippets

## Snippet 1

Context: `src/chainstate/stacks/db/blocks.rs:928` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

        // hashes are contiguous enough -- for each seqnum, there is a block with seqnum+1 with the
        // block at seqnum as its parent.  There may be more than one.
```
After
```rust
}

        // sanity check -- all parent block hashes are unique.  If there are duplicates, then the
        // miner equivocated.
        let mut parent_hashes : HashMap<BlockHeaderHash, StacksMicroblockHeader> = HashMap::new();
        for i in 0..signed_microblocks.len() {
            let signed_microblock = &signed_microblocks[i];
            if parent_hashes.contains_key(&signed_microblock.header.prev_block) {
```

## Snippet 2

Context: `src/net/mod.rs:1010` (changes the branch that decides whether execution stops or continues)

Before
```rust
pub fn add_empty_burnchain_block(&mut self) -> u64 {
            let empty_block = {
                let mut burndb = self.burndb.take().unwrap();
                let sn = BurnDB::get_canonical_burn_chain_tip(burndb.conn()).unwrap();
                let empty_block = self.empty_burnchain_block(sn.block_height);
```
After
```rust
pub fn add_empty_burnchain_block(&mut self) -> u64 {
            let empty_block = {
                let burndb = self.burndb.take().unwrap();
                let sn = BurnDB::get_canonical_burn_chain_tip(burndb.conn()).unwrap();
                let empty_block = self.empty_burnchain_block(sn.block_height);
```

## Snippet 3

Context: `src/burnchains/burnchain.rs:1370` (changes a sensitive control or state-update path)

Before
```rust
// sentinel block hash.  This is because epochs 121, 122, and 123 don't have any block
            // commits.
            let mut expected_winning_hashes = vec![
                BlockHeaderHash([0u8; 32]),
                block_124_winners[scenario_idx].block_header_hash.clone()
```
After
```rust
// sentinel block hash.  This is because epochs 121, 122, and 123 don't have any block
            // commits.
            let expected_winning_hashes = vec![
                BlockHeaderHash([0u8; 32]),
                block_124_winners[scenario_idx].block_header_hash.clone()
```

## Snippet 4

Context: `src/chainstate/stacks/transaction.rs:246` (changes a sensitive control or state-update path)

Before
```rust
}

                // must have the same sequence number and block parent
                if h1.sequence != h2.sequence || h1.prev_block != h2.prev_block {
                    return Err(net_error::DeserializeError);
                }
```
After
```rust
}

                // must have the same sequence number or same block parent
                if h1.sequence != h2.sequence && h1.prev_block != h2.prev_block {
                    return Err(net_error::DeserializeError);
                }
```

# Fix Pattern

Align detection and deserialization with the same equivocation predicate: distinct signed microblock headers conflict if they share sequence number or parent block hash.

## How It Was Fixed

The patch adds duplicate-parent detection in validate_parent_microblock_stream and changes PoisonMicroblock deserialization from requiring both matching sequence and matching parent to accepting either matching sequence or matching parent.

# Why It Matters

1. Keeps microblock fork detection aligned with the stated protocol rule.

2. Prevents duplicate-parent signed microblock evidence from being ignored by this validation path.

3. Avoids overstating impact beyond equivocation evidence handling.

# Evidence Notes

The supported evidence is concentrated in src/chainstate/stacks/db/blocks.rs and src/chainstate/stacks/transaction.rs. The net/mod.rs and burnchain.rs hunks are mutability cleanup in helper or test code and do not support security claims. The evidence does not support the heuristic panic, malformed-input denial-of-service, reward, slashing, or remote exploitability claims. Protocol security invariant: Two distinct, well-formed, signed microblock headers are conflicting equivocation evidence if they share either the same sequence number or the same parent block hash; PoisonMicroblock validation must accept both conflict shapes. Verification notes: The patch does not prove remote exploitability or a node crash condition. The patch does not show malformed input reaching a panic-prone conversion path. The patch does not establish economic impact, slashing behavior, or miner reward consequences beyond equivocation evidence handling. The warning and unit-test cleanup hunks should not be counted as security fixes. Code evidence directly shows duplicate prev_block detection was added. Code evidence directly shows PoisonMicroblock acceptance changed from same sequence and parent to same sequence or parent. No provided tests or external protocol documentation prove economic impact or exploitability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `protocol-equivocation-detection-gap`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `protocol, consensus, microblocks, equivocation, validation, poison-evidence`

The provided patch clearly tightens a protocol-sensitive equivocation predicate for signed microblocks: duplicate parent hashes are now detected as miner equivocation, and PoisonMicroblock payload validation now accepts evidence when headers share either sequence number or parent block hash. This supports keeping the case as security hardening, but the evidence does not prove a concrete exploit, liveness failure, slashing outcome, or economic impact strongly enough to retain the original security-fix/high-confidence framing.

## Security Evidence

1. Microblock stream validation now tracks prev_block values and treats duplicate parents as deliberate microblock forks.
2. The code returns a PoisonMicroblock payload when duplicate signed microblock parents are observed.
3. PoisonMicroblock deserialization changed from requiring same sequence and same parent to accepting same sequence or same parent.
4. Commit subject explicitly states the protocol rule for microblock conflicts was broadened to either same parent or same sequence number.

## Missing Evidence

1. No proof that the prior behavior caused a concrete exploit or externally triggerable failure.
2. No provided protocol documentation showing exact security consequences of missing duplicate-parent poison evidence.
3. No evidence of reward theft, slashing bypass, chain halt, or consensus split impact.
4. Several hunks are warning or unit-test cleanup and do not support security claims.

## Claim Boundaries

1. Validated only as hardening of microblock equivocation detection and poison evidence acceptance.
2. Do not claim malformed-input denial of service, panic safety, or remote code execution.
3. Do not claim specific economic or slashing consequences from the provided patch alone.
4. The original liveness-failure classification is too specific for the supplied evidence.
