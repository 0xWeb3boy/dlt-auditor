---
case_id: case_20240227_a7e114be3c
project: stacks-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: p2p-networking
source_quality: high
date: 2024-02-27
source_refs:
  - git:a7e114be3ca187e3f757a6bb463e064eb478acd8
  - "stacks-signer/src/signer.rs:1225"
  - "stacks-signer/src/signer.rs:743"
  - "testnet/stacks-node/src/nakamoto_node/miner.rs:333"
  - "stackslib/src/chainstate/nakamoto/signer_set.rs:488"
bug_class: inconsistent-signer-transaction-validation
impact_type:
  - transaction-integrity
  - replay-resistance
confidence: medium
tags:
  - signer-transactions
  - nonce-validation
  - consensus
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to centralize vote-transaction filtering in `NakamotoSigners` and apply that shared logic from signer and miner paths. This may be security relevant because it touches signer transaction validation, but the supplied evidence does not prove that invalid transactions could be executed, finalized, replayed, or used to cause a consensus failure before the patch.

## Observed Patch Facts

1. In `stacks-signer/src/signer.rs`, the patch removes `fn parse_vote_for_aggregate_public_key(`.

2. In `stacks-signer/src/signer.rs`, the patch replaces `.get_next_transactions_with_retry(&self.next_signer_ids)?` with `.get_next_transactions_with_retry(&self.next_signer_ids)?;`.

3. In `testnet/stacks-node/src/nakamoto_node/miner.rs`, the patch replaces `// There may be more than signer messages, but odds are there is only one transacton...` with `if signer_messages.is_empty() {`.

4. In `stackslib/src/chainstate/nakamoto/signer_set.rs`, the patch adds `/// Verify that the transaction is a valid vote for the aggregate public key`.

## Project Context

The changed code sits primarily in `stacks-signer/src`, `testnet/stacks-node/src/nakamoto_node`, `testnet/stacks-node/src`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `stackslib/src/chainstate/nakamoto/miner.rs`, `stackslib/src/chainstate/nakamoto/tenure.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stackslib/src/chainstate/nakamoto/miner.rs`, `testnet/stacks-node/src/node.rs`. The strongest project-level identifiers around this patch are `transaction`, `account_nonces`, `TransactionPayload::ContractCall`, and `payload`. Nearby tests or test-like files include `stackslib/src/chainstate/nakamoto/tests/mod.rs`, `testnet/stacks-node/src/tests/neon_integrations.rs`.

## Before/After Behavior

Before the patch, signer-side transaction retrieval used signer-local validation, while the miner path is shown collecting signer messages and iterating transactions without evidence of the same shared validation. After the patch, validation/filtering is moved into `stackslib/src/chainstate/nakamoto/signer_set.rs`, signer retrieval delegates to shared filtering, and the miner path obtains account nonces before signer transaction selection.

# Root Cause

Not established as a vulnerability. The grounded issue is duplicated or non-uniform signer vote-transaction filtering across components, with the patch moving that logic into a shared helper and applying it more broadly.

## Walkthrough

1. Signer transaction data is retrieved from StackerDB for next signer processing.

2. The old signer path had local vote parsing and validation logic.

3. The patch removes signer-local parsing from `stacks-signer/src/signer.rs` and adds shared validation in `NakamotoSigners`.

4. The added validator is documented as checking valid formation, expected address, and nonce, while not validating vote function arguments.

5. The signer path now delegates filtering to shared Nakamoto signer filtering state.

6. The miner path now prepares signer account nonce state before processing signer-provided transactions.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stackslib/src/chainstate/nakamoto/signer_set.rs | 488 | Defines shared `valid_vote_transaction` logic for expected signer address, nonce, and vote-contract transaction shape. |
| stacks-signer/src/signer.rs | 730 | Signer expected-transaction retrieval now delegates filtering to the shared Nakamoto signer validation path. |
| testnet/stacks-node/src/nakamoto_node/miner.rs | 301 | Miner reads signer messages from StackerDB and now prepares signer account nonce state before transaction inclusion. |
| testnet/stacks-node/src/nakamoto_node/miner.rs | 333 | Miner-side signer transaction selection is changed from unfiltered message collection toward validation against expected signer nonces. |

## Code Snippets

## Snippet 1

Context: `stacks-signer/src/signer.rs:1225` (changes an authorization or privilege gate)

Before
```rust
Ok(())
    }

    fn parse_vote_for_aggregate_public_key(
        transaction: &StacksTransaction,
    ) -> Option<(u64, Point, u64, u64)> {
        let TransactionPayload::ContractCall(payload) = &transaction.payload else {
            // Not a contract call so not a special cased vote for aggregate public key transaction
```
After
```rust
Ok(())
    }
}
```

## Snippet 2

Context: `stacks-signer/src/signer.rs:743` (changes a sensitive control or state-update path)

Before
```rust
let transactions: Vec<_> = self
            .stackerdb
            .get_next_transactions_with_retry(&self.next_signer_ids)?
            .into_iter()
            .filter_map(|tx| {
                if !self.valid_vote_transaction(&account_nonces, &tx) {
                    return None;
                }
```
After
```rust
let transactions: Vec<_> = self
            .stackerdb
            .get_next_transactions_with_retry(&self.next_signer_ids)?;
        let mut filtered_transactions = std::collections::HashMap::new();
        NakamotoSigners::update_filtered_transactions(
            &mut filtered_transactions,
            &account_nonces,
            self.mainnet,
```

## Snippet 3

Context: `testnet/stacks-node/src/nakamoto_node/miner.rs:333` (changes signature or replay validation logic)

Before
```rust
.collect();

        // There may be more than signer messages, but odds are there is only one transacton per signer
        let mut transactions_to_include = Vec::with_capacity(signer_messages.len());
        for (_slot, signer_message) in signer_messages {
            match signer_message {
                SignerMessage::Transactions(transactions) => {
                    for transaction in transactions {
```
After
```rust
.collect();

        if signer_messages.is_empty() {
            return Ok(vec![]);
        }

        // Get all nonces for the signers from clarity DB to use to validate transactions
        let account_nonces = chainstate
```

## Snippet 4

Context: `stackslib/src/chainstate/nakamoto/signer_set.rs:488` (changes signature or replay validation logic)

Before
```rust
Ok(signers)
    }
}
```
After
```rust
Ok(signers)
    }

    /// Verify that the transaction is a valid vote for the aggregate public key
    /// Note: it does not verify the function arguments, only that the transaction is validly formed
    /// and has a valid nonce from an expected address
    pub fn valid_vote_transaction(
        account_nonces: &HashMap<StacksAddress, u64>,
```

# Fix Pattern

Centralize duplicated validation/filtering logic in a shared helper and route multiple consumers through it.

## How It Was Fixed

The patch adds shared vote-transaction validation/filtering under `NakamotoSigners`, updates signer-side expected transaction retrieval to use shared filtered state, and changes miner-side signer transaction handling to obtain nonce state and use the shared validation model.

# Why It Matters

1. Reduces divergence between signer and miner handling of signer-supplied transactions.

2. Address and nonce checks are relevant to replay and stale transaction rejection.

3. Security impact is plausible but not demonstrated by the supplied evidence.

# Evidence Notes

Evidence supports a refactor/hardening of signer transaction validation, especially in `stackslib/src/chainstate/nakamoto/signer_set.rs`, `stacks-signer/src/signer.rs`, and `testnet/stacks-node/src/nakamoto_node/miner.rs`. It does not establish exploitability, consensus impact, remote attacker control, or that invalid transactions were previously accepted into finalized blocks. Protocol security invariant: Potential invariant: signer-supplied aggregate-public-key vote transactions should be validated consistently by consumers, including checks for expected signer address and nonce. The provided evidence does not establish that violating this invariant previously led to an exploitable security impact. Verification notes: The patch does not show validation of vote function arguments; comments explicitly say only formation, expected address, and nonce are checked. The evidence does not prove that invalid signer transactions could be executed or finalized before the patch. The evidence does not establish remote exploitability or a consensus split scenario. The change may also be API cleanup through centralizing validation, but miner adoption gives it security-relevant hardening weight. No evidence shows a pre-patch exploit path. No evidence shows invalid signer transactions being executed or finalized. No evidence shows a consensus split or privilege bypass. Tests were changed, but their exact assertions are not provided. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `inconsistent-signer-transaction-validation`
Final impact type: `transaction-integrity, replay-resistance`
Final confidence: `medium`
Final tags: `signer-transactions, nonce-validation, consensus, security-hardening`

The supplied evidence supports retaining this as security hardening, not as a proven security fix. The patch moves signer vote transaction validation into shared Nakamoto signer logic and applies filtering more broadly, including miner-side handling of signer-provided transactions. The added checks around expected signer address, nonce, contract-call shape, and vote function are security-sensitive because they constrain replay/stale or unexpected signer transactions, but the evidence does not prove a concrete exploit, finalized invalid transaction, or consensus failure before the change.

## Security Evidence

1. Adds shared valid_vote_transaction logic for aggregate public key vote transactions.
2. Validation checks expected signer address and valid nonce from account_nonces.
3. Signer transaction retrieval now routes through NakamotoSigners::update_filtered_transactions.
4. Miner path now obtains signer account nonces before selecting signer transactions.
5. Changed code is in signer, miner, and Nakamoto signer-set paths tied to consensus-sensitive signer transaction handling.

## Missing Evidence

1. No proof that invalid signer transactions were accepted into finalized blocks before the patch.
2. No demonstrated remote attacker control or exploit path.
3. No evidence of consensus split, privilege escalation, or state corruption.
4. Tests are mentioned but their assertions are not supplied.
5. The added comment states vote function arguments are not validated.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix.
2. Do not claim a concrete exploitable vulnerability from the supplied patch alone.
3. Do not retain the original state-corruption framing as proven.
4. Impact should be limited to signer transaction integrity and replay/stale transaction resistance.
