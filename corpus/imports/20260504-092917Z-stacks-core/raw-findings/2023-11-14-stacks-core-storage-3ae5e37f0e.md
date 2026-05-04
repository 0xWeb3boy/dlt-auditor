---
case_id: case_20231114_3ae5e37f0e
project: stacks-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2023-11-14
source_refs:
  - git:3ae5e37f0e4f5165975ed83d377c92832efb0def
  - "stackslib/src/chainstate/nakamoto/mod.rs:1360"
  - "stackslib/src/chainstate/burn/db/sortdb.rs:1929"
  - "testnet/stacks-node/src/mockamoto.rs:458"
  - "stackslib/src/chainstate/nakamoto/mod.rs:255"
bug_class: cryptographic-signature-type-hardening
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - consensus
  - signature
  - schnorr
  - block-validation
  - type-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Nakamoto stacker signatures from a generic `MessageSignature` placeholder to `SchnorrSignature`, converts them to `WSTSSignature` in `accept_block`, and rejects blocks whose stacker signature cannot be converted. This is plausibly security relevant because it affects consensus block acceptance and cryptographic signature representation, but the provided evidence does not establish that the old code accepted invalid blocks, bypassed signature verification, or caused a consensus vulnerability.

## Observed Patch Facts

1. In `stackslib/src/chainstate/nakamoto/mod.rs`, the patch replaces `if !sortdb.expects_stacker_signature(` with `let schnorr_signature = block.header.stacker_signature.to_wsts_signature().ok_or({`.

2. In `stackslib/src/chainstate/burn/db/sortdb.rs`, the patch replaces `_stacker_signature: &MessageSignature,` with `_stacker_signature: &WSTSSignature,`.

3. In `testnet/stacks-node/src/mockamoto.rs`, the patch replaces `stacker_signature: MessageSignature([0; 65]),` with `stacker_signature: SchnorrSignature::default(),`.

4. In `stackslib/src/chainstate/nakamoto/mod.rs`, the patch replaces `/// Recoverable ECDSA signature from the stacker set active during the tenure.` with `/// Schnorr signature over the block header from the stacker set active during the te...`.

## Project Context

The changed code sits primarily in `stackslib/src/chainstate/nakamoto`, `stackslib/src/chainstate`, `stackslib/src/chainstate/burn/db`, which anchors the finding in the `storage` area of the project. Historical context from `stackslib/src/chainstate/nakamoto/miner.rs`, `testnet/stacks-node/src/node.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stackslib/src/chainstate/nakamoto/miner.rs`, `stackslib/src/chainstate/stacks/mod.rs`. The strongest project-level identifiers around this patch are `block`, `stacker_signature`, `MessageSignature`, and `header`. Nearby tests or test-like files include `stackslib/src/chainstate/stacks/tests/block_construction.rs`, `stackslib/src/chainstate/nakamoto/tests/mod.rs`.

## Before/After Behavior

Before the patch, `NakamotoBlockHeader.stacker_signature` was a `MessageSignature` placeholder and `accept_block` passed it directly to `sortdb.expects_stacker_signature`, whose API accepted `&MessageSignature`. After the patch, the header field is `SchnorrSignature`; `accept_block` converts it with `to_wsts_signature()` and returns `InvalidStacksBlock` if conversion fails; `expects_stacker_signature` now accepts `&WSTSSignature`. Mock construction was updated accordingly.

# Root Cause

The grounded issue is a type-level mismatch: the stacker-set signature field used the same generic recoverable ECDSA-style `MessageSignature` representation as miner signatures, despite the surrounding comments and new code indicating the stacker signature should be Schnorr/WSTS. The evidence does not prove this mismatch was exploitable.

## Walkthrough

1. A Nakamoto block reaches `NakamotoChainState::accept_block`.

2. Before the change, the stacker signature was stored as `MessageSignature` and passed directly to the sortition DB expectation check.

3. The header comments described the stacker signature as an ECDSA placeholder, while the patched code describes it as a Schnorr signature from the active stacker set.

4. After the change, the header stores `stacker_signature` as `SchnorrSignature`.

5. `accept_block` attempts to convert that value to `WSTSSignature`.

6. If conversion fails, the block is rejected with `ChainstateError::InvalidStacksBlock`.

7. The sortition DB API now takes `&WSTSSignature` instead of `&MessageSignature`.

8. The provided excerpt still shows the sortition DB parameter as underscored, so the evidence does not prove how or whether the signature value is compared inside that function.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stackslib/src/chainstate/nakamoto/mod.rs | 255 | Defines NakamotoBlockHeader.stacker_signature as SchnorrSignature instead of the generic MessageSignature placeholder. |
| stackslib/src/chainstate/nakamoto/mod.rs | 1360 | During block acceptance, converts the header stacker_signature to a WSTS signature and rejects blocks with no stacker signature before checking active-cycle expectations. |
| stackslib/src/chainstate/burn/db/sortdb.rs | 1929 | Updates the sortition DB active-cycle signature expectation API to accept WSTSSignature instead of MessageSignature. |
| testnet/stacks-node/src/mockamoto.rs | 458 | Updates mock Nakamoto block construction to populate a SchnorrSignature default for stacker_signature. |

## Code Snippets

## Snippet 1

Context: `stackslib/src/chainstate/nakamoto/mod.rs:1360` (changes signature or replay validation logic)

Before
```rust
};

        if !sortdb.expects_stacker_signature(
            &block.header.consensus_hash,
            &block.header.stacker_signature,
        )? {
            let msg = format!("Received block, but the stacker signature does not match the active stacking cycle");
            warn!("{}", msg);
```
After
```rust
};

        let schnorr_signature = block.header.stacker_signature.to_wsts_signature().ok_or({
            let msg =
                format!("Received block, signed by miner, but the block has no stacker signature");
            warn!("{}", msg);
            ChainstateError::InvalidStacksBlock(msg)
        })?;
```

## Snippet 2

Context: `stackslib/src/chainstate/burn/db/sortdb.rs:1929` (changes a sensitive control or state-update path)

Before
```rust
&self,
        consensus_hash: &ConsensusHash,
        _stacker_signature: &MessageSignature,
    ) -> Result<bool, db_error> {
        let sn = SortitionDB::get_block_snapshot(self, &self.context.chain_tip)?
```
After
```rust
&self,
        consensus_hash: &ConsensusHash,
        _stacker_signature: &WSTSSignature,
    ) -> Result<bool, db_error> {
        let sn = SortitionDB::get_block_snapshot(self, &self.context.chain_tip)?
```

## Snippet 3

Context: `testnet/stacks-node/src/mockamoto.rs:458` (changes a sensitive control or state-update path)

Before
```rust
tx_merkle_root: tx_merkle_tree.root(),
                state_index_root,
                stacker_signature: MessageSignature([0; 65]),
                miner_signature: MessageSignature([0; 65]),
                consensus_hash: sortition_tip.consensus_hash.clone(),
                parent_block_id: StacksBlockId::new(&chain_tip_ch, &chain_tip_bh),
```
After
```rust
tx_merkle_root: tx_merkle_tree.root(),
                state_index_root,
                stacker_signature: SchnorrSignature::default(),
                miner_signature: MessageSignature::empty(),
                consensus_hash: sortition_tip.consensus_hash.clone(),
                parent_block_id: StacksBlockId::new(&chain_tip_ch, &chain_tip_bh),
```

## Snippet 4

Context: `stackslib/src/chainstate/nakamoto/mod.rs:255` (changes a sensitive control or state-update path)

Before
```rust
/// Recoverable ECDSA signature from the tenure's miner.
    pub miner_signature: MessageSignature,
    /// Recoverable ECDSA signature from the stacker set active during the tenure.
    /// TODO: This is a placeholder
    pub stacker_signature: MessageSignature,
}
```
After
```rust
/// Recoverable ECDSA signature from the tenure's miner.
    pub miner_signature: MessageSignature,
    /// Schnorr signature over the block header from the stacker set active during the tenure.
    pub stacker_signature: SchnorrSignature,
}
```

# Fix Pattern

Replace a generic placeholder cryptographic type with a protocol-specific signature type and add an explicit conversion/presence check before downstream consensus validation continues.

## How It Was Fixed

The patch changed `NakamotoBlockHeader.stacker_signature` to `SchnorrSignature`, updated its documentation, added `to_wsts_signature()` conversion and rejection in `accept_block`, changed `expects_stacker_signature` to accept `&WSTSSignature`, and updated testnet mock block construction to use `SchnorrSignature::default()`.

# Why It Matters

1. Consensus block acceptance is a sensitive path.

2. Protocol-specific signature types reduce accidental misuse.

3. The new rejection handles missing or non-convertible stacker signatures.

4. The evidence supports hardening or correctness, not a proven vulnerability fix.

# Evidence Notes

Strong evidence supports a representation and API change in `stackslib/src/chainstate/nakamoto/mod.rs` and `stackslib/src/chainstate/burn/db/sortdb.rs`. The claim that this fixed a security vulnerability is not established: there is no shown exploit, no shown acceptance of invalid signatures, no advisory language, and the shown `expects_stacker_signature` parameter remains `_stacker_signature`, which weakens claims about actual signature validation. The mock file is support code, not root-cause evidence. Protocol security invariant: If enforced, Nakamoto block acceptance should require the stacker signature to be represented as the protocol-specific Schnorr/WSTS signature type before active-cycle expectation checks. The provided evidence shows type and conversion changes, but not a demonstrated verification bypass or exploit path. Verification notes: The patch does not prove that arbitrary invalid Schnorr signatures were previously accepted. The patch does not prove a consensus split, chain reorganization, or funds-at-risk exploit path. The shown sortdb function still names the signature parameter with an underscore, so actual signature comparison is not proven from the evidence. The testnet/mock change is support code and is not itself evidence of a production vulnerability. Downgraded from likely security-hardening to unclear because exploitability is not shown. Downgraded confidence to low for security classification, while preserving the grounded consensus-signature type mismatch. Set `keep_in_security_corpus` to false under the rule for security-relevant but unproven vulnerability theses. Rejected unsupported claims about state corruption, storage corruption, replay impact, consensus split, or funds at risk. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cryptographic-signature-type-hardening`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `consensus, signature, schnorr, block-validation, type-hardening`

The evidence supports security-hardening, not a proven security-fix. The patch moves a consensus block header stacker signature from a generic ECDSA-style placeholder type to a Schnorr-specific type, converts it to a WSTS signature during block acceptance, and rejects blocks whose stacker signature cannot be converted. That clearly tightens security-sensitive consensus signature handling, but the provided excerpts do not prove that invalid blocks were previously accepted or that an exploitable vulnerability existed.

## Security Evidence

1. NakamotoBlockHeader.stacker_signature changes from MessageSignature placeholder to SchnorrSignature.
2. accept_block now converts stacker_signature with to_wsts_signature() before continuing consensus acceptance.
3. accept_block now returns InvalidStacksBlock when the stacker signature cannot be converted or is absent.
4. Sortition DB expectation API now requires WSTSSignature instead of MessageSignature.

## Missing Evidence

1. No advisory, CVE, exploit description, or commit message indicating a vulnerability fix.
2. No shown test proving previously accepted invalid stacker signatures are now rejected.
3. The expects_stacker_signature parameter is still shown as underscored, so actual signature comparison is not proven from the excerpt.
4. No evidence of state corruption, replay, consensus split, or funds-at-risk impact.

## Claim Boundaries

1. Treat as consensus signature hardening, not a confirmed vulnerability fix.
2. Do not claim arbitrary invalid Schnorr signatures were previously accepted.
3. Do not claim storage or snapshot state corruption from the supplied evidence.
4. Do not claim concrete exploitability beyond stricter signature representation and presence checking.
