---
case_id: case_20240214_5ad797514e
project: stacks-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-02-14
source_refs:
  - git:5ad797514e1336758eccfdf6d8b3152202da5ce8
  - "testnet/stacks-node/src/nakamoto_node/miner.rs:284"
  - "testnet/stacks-node/src/nakamoto_node/miner.rs:334"
  - "testnet/stacks-node/src/nakamoto_node/miner.rs:437"
  - "testnet/stacks-node/src/nakamoto_node/miner.rs:497"
bug_class: signer-message-validation
impact_type:
  - protocol-integrity
  - authorization-bypass-hardening
confidence: medium
tags:
  - validator-ops
  - signer-message-validation
  - transaction-filtering
  - rejection-accounting
  - protocol-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Nakamoto miner/signer coordination logic in testnet/stacks-node/src/nakamoto_node/miner.rs. It builds a signer slot-to-address map, filters signer-submitted transactions by origin address, begins nonce-related chainstate handling, and changes rejection accounting to use signer weights while skipping already-seen signer IDs. These are plausibly security-adjacent protocol correctness changes, but the evidence does not prove attacker control, acceptance of invalid transactions, consensus failure, fund loss, or a standalone vulnerability.

## Observed Patch Facts

1. In `testnet/stacks-node/src/nakamoto_node/miner.rs`, the patch replaces `// Get the block slot for every signer` with `// Get the slots for every signer`.

2. In `testnet/stacks-node/src/nakamoto_node/miner.rs`, the patch replaces `// TODO: filter out transactons that are not valid and that do not come from the signers` with `for transaction in transactions {`.

3. In `testnet/stacks-node/src/nakamoto_node/miner.rs`, the patch replaces `// Ensure that we do not double count a rejection from the same signer.` with `if rejections.contains(&signer_id) {`.

4. In `testnet/stacks-node/src/nakamoto_node/miner.rs`, the patch replaces `let signature = self` with `let reward_cycle = self`.

## Project Context

The changed code sits primarily in `testnet/stacks-node/src/nakamoto_node`, `testnet/stacks-node/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `testnet/stacks-node/src/nakamoto_node/relayer.rs`, `testnet/stacks-node/src/nakamoto_node/peer.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `testnet/stacks-node/src/run_loop/neon.rs`, `testnet/stacks-node/src/mockamoto.rs`. The strongest project-level identifiers around this patch are `from`, `signers`, `signer`, and `transaction`. Nearby tests or test-like files include `testnet/stacks-node/src/tests/signer.rs`, `testnet/stacks-node/src/tests/nakamoto_integrations.rs`.

## Before/After Behavior

Before the patch, signer transaction messages were appended wholesale in the shown get_signer_transactions path. After the patch, transactions are iterated individually, their origin address and nonce are read, and transactions from addresses outside the active signer address set are skipped. Before the patch, rejection handling used a set of signer IDs and a count-based threshold in the shown excerpt. After the patch, already-seen signer IDs are skipped before additional rejection accounting, and the surrounding path loads reward-cycle signer weights for weighted rejection handling.

# Root Cause

The supported root cause is incomplete local validation/accounting in the miner's signer-message consumption path. The prior code shown did not filter signer-submitted transaction lists by active signer address in this function, and the rejection path was being changed from count-based set tracking toward explicit once-per-signer weighted accounting. A stronger claim of an exploitable vulnerability is not supported by the provided evidence.

## Walkthrough

1. The miner derives a signers contract for the relevant reward cycle and message ID.

2. The helper now builds a HashMap from signer slot ID to signer address instead of only returning slot IDs.

3. The transaction collection path reads latest chunks from the signer StackerDB slots and decodes SignerMessage values.

4. In the prior shown code, SignerMessage::Transactions caused the entire transaction vector to be appended for inclusion.

5. In the patched code, each transaction is inspected individually.

6. Transactions whose origin address is not in the derived active signer address set are logged and skipped.

7. The patch also reads the transaction nonce and starts a chainstate current-nonce lookup, but the provided excerpt is insufficient to fully describe the nonce acceptance rule.

8. The rejection path now checks whether a signer_id was already seen before doing further rejection handling.

9. The broadcast/signature path now computes the reward cycle and loads signer weights for the active signer set.

10. The evidence supports protocol hardening or correctness, but not a confirmed vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| testnet/stacks-node/src/nakamoto_node/miner.rs | 262 | Builds the signer contract and signer slot-to-address map used to validate signer-channel messages. |
| testnet/stacks-node/src/nakamoto_node/miner.rs | 305 | Reads signer transaction messages and filters included transactions by signer address and account nonce state. |
| testnet/stacks-node/src/nakamoto_node/miner.rs | 431 | Handles signer block rejections and prevents duplicate rejection accounting for the same signer. |
| testnet/stacks-node/src/nakamoto_node/miner.rs | 478 | Loads reward-cycle signer weights used by the block proposal rejection threshold logic. |

## Code Snippets

## Snippet 1

Context: `testnet/stacks-node/src/nakamoto_node/miner.rs:284` (changes persisted or aggregate state handling)

Before
```rust
));
        };
        // Get the block slot for every signer
        let slot_ids = stackerdbs
            .get_signers(&signers_contract_id)
            .expect("FATAL: could not get signers from stacker DB")
            .iter()
            .enumerate()
```
After
```rust
));
        };
        // Get the slots for every signer
        let signers = stackerdbs
            .get_signers(&signers_contract_id)
            .expect("FATAL: could not get signers from stacker DB");
        let mut slot_ids_addresses = HashMap::with_capacity(signers.len());
        for (slot_id, address) in stackerdbs
```

## Snippet 2

Context: `testnet/stacks-node/src/nakamoto_node/miner.rs:334` (changes signature or replay validation logic)

Before
```rust
match signer_message {
                SignerMessage::Transactions(transactions) => {
                    // TODO: filter out transactons that are not valid and that do not come from the signers
                    // TODO: move this filter function from stacks-signer and make it globally available perhaps?
                    transactions_to_include.extend(transactions);
                }
                _ => {} // Any other message is ignored
            }
```
After
```rust
match signer_message {
                SignerMessage::Transactions(transactions) => {
                    for transaction in transactions {
                        let address = transaction.origin_address();
                        let nonce = transaction.get_origin_nonce();
                        if !addresses.contains(&address) {
                            test_debug!("Miner: ignoring transaction ({:?}) with nonce {nonce} from address {address}", transaction.txid());
                            continue;
```

## Snippet 3

Context: `testnet/stacks-node/src/nakamoto_node/miner.rs:437` (changes the branch that decides whether execution stops or continues)

Before
```rust
}
                        } else {
                            // We received a rejection that is not signed. We will keep waiting for a threshold number of rejections.
                            // Ensure that we do not double count a rejection from the same signer.
                            rejections.insert(signer_id);
                            if rejections.len() > rejection_threshold {
                                // A threshold number of signers rejected the proposed block.
                                // Miner will likely never get a signed block from the signers for this particular block
```
After
```rust
}
                        } else {
                            if rejections.contains(&signer_id) {
                                // We have already received a rejection from this signer
                                continue;
                            }

                            // We received a rejection that is not signed. We will keep waiting for a threshold number of rejections.
```

## Snippet 4

Context: `testnet/stacks-node/src/nakamoto_node/miner.rs:497` (changes the branch that decides whether execution stops or continues)

Before
```rust
&block,
        )?;
        let signature = self
            .wait_for_signer_signature(
```
After
```rust
&block,
        )?;

        let reward_cycle = self
            .burnchain
            .block_height_to_reward_cycle(self.burn_block.block_height)
            .expect("FATAL: no reward cycle for burn block");
        let signer_weights =
```

# Fix Pattern

Add local validation and accounting checks at signer-message consumption boundaries: derive active signer identities, filter transaction messages by authorized origin address, and account for signer rejections with explicit duplicate handling and signer weights.

## How It Was Fixed

The patch updates miner.rs so signer slots are paired with signer addresses, then uses those addresses when processing signer transaction messages. It replaces wholesale extension of the transaction inclusion list with per-transaction checks and skips non-signer-origin transactions. It also adjusts rejection handling to skip already-seen signer IDs before weighted rejection accounting and loads reward-cycle signer weights before waiting for signer signatures.

# Why It Matters

1. Signer messages influence miner block proposal behavior.

2. Filtering by active signer address reduces reliance on unvalidated message contents.

3. Weighted rejection accounting better matches signer-set semantics than raw count-based logic.

4. The provided evidence does not show an externally exploitable path.

5. This should not be kept as a confirmed vulnerability fix without stronger proof.

# Evidence Notes

Grounded evidence comes from testnet/stacks-node/src/nakamoto_node/miner.rs around lines 262, 305, 431, and 478. The strongest evidence is the replacement of transactions_to_include.extend(transactions) with per-transaction origin-address handling and an address membership check. The signer slot-to-address map and signer weight loading are also shown. Unsupported or overstated claims include non-signer write access to StackerDB chunks, downstream acceptance of invalid transactions, consensus split, fund loss, block forgery, cryptographic break, and duplicate-prone rejection counting before the patch, because the prior code already used a set in the shown excerpt. Protocol security invariant: The Nakamoto miner's signer-message handling should consume signer-channel data consistently with the active signer set, including using the correct signer slot/address mapping and avoiding repeated accounting for the same signer when rejection weights are tracked. The provided evidence shows changes in this direction but does not establish an exploitable security violation. Verification notes: The patch does not prove that non-signers can write signer StackerDB chunks. The patch does not prove that invalid included transactions would be accepted by later chainstate validation. The patch does not prove a consensus split, fund loss, or block forgery exploit. The patch does not show whether the changed tests are regression tests for a security issue versus protocol correctness. The evidence supports signer-message validation and threshold-accounting hardening, not a standalone cryptographic break. No exploit scenario is demonstrated in the provided evidence. No proof is provided that invalid transactions would pass later validation. No proof is provided that attackers can inject signer chunks. Nonce validation details are only partially visible in the excerpt. Changed tests may indicate correctness regression coverage, but their security intent is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signer-message-validation`
Final impact type: `protocol-integrity, authorization-bypass-hardening`
Final confidence: `medium`
Final tags: `validator-ops, signer-message-validation, transaction-filtering, rejection-accounting, protocol-hardening`

The supplied patch evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. The miner previously accepted signer transaction messages wholesale and the patch adds active-signer address filtering plus nonce-related handling. It also changes signer rejection accounting toward once-per-signer weighted handling. These are security-sensitive protocol-boundary checks, but the evidence does not prove attacker write access, downstream acceptance of invalid transactions, consensus failure, fund loss, or another concrete exploit.

## Security Evidence

1. SignerMessage::Transactions changed from wholesale transactions_to_include.extend(transactions) to per-transaction inspection.
2. Patched code derives active signer addresses and skips transactions whose origin address is not in that signer set.
3. Patched code reads transaction nonces and begins chainstate nonce handling in the signer transaction path.
4. Block rejection handling now skips already-seen signer IDs before further rejection accounting.
5. Patch loads reward-cycle signer weights for rejection threshold logic, indicating quorum/accounting semantics were tightened.

## Missing Evidence

1. No proof that non-signers or attackers can write the relevant signer StackerDB chunks.
2. No proof that invalid or non-signer-origin transactions would pass later chainstate validation.
3. No demonstrated exploit scenario, consensus split, fund loss, block forgery, or denial of service.
4. Nonce acceptance rule is only partially visible in the supplied evidence.
5. Changed tests are not shown enough to establish security intent.

## Claim Boundaries

1. Classify as hardening of signer-message validation and rejection accounting, not a confirmed exploitable security bug.
2. Do not claim state corruption, cryptographic break, replay vulnerability, fund loss, or consensus failure from this evidence alone.
3. Do not claim duplicate rejection counting was definitely exploitable; the before excerpt already used a set, while the after evidence mainly supports weighted accounting hardening.
4. The evidence supports a security-sensitive boundary tightening in miner/signer coordination.
