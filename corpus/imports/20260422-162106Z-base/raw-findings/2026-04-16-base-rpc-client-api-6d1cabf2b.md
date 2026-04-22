---
case_id: case_20260416_6d1cabf2b
project: base
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2026-04-16
source_refs:
  - git:6d1cabf2b1bdd012ffd518033e2c43feba8ba479
  - "crates/proof/challenge/src/driver.rs:412"
  - "crates/proof/contracts/src/aggregate_verifier.rs:188"
  - "crates/proof/contracts/src/aggregate_verifier.rs:406"
  - "crates/proof/contracts/src/aggregate_verifier.rs:57"
bug_class: incorrect-fraud-challenge-validation
impact_type:
  - integrity
confidence: medium
tags:
  - blockchain-core
  - challenger
  - dispute-handling
  - fraud-proof
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a correctness fix in the off-chain challenger: the `FraudulentZkChallenge` path previously used full intermediate-root validation and a first-invalid-index heuristic, and now validates only the challenged root. That establishes a logic error in challenge handling, but the provided code and commit text do not prove an exploitable vulnerability, an on-chain flaw, or concrete security impact beyond incorrect skip behavior in this service.

## Observed Patch Facts

1. In `crates/proof/challenge/src/driver.rs`, the patch replaces `let (result, intermediate_roots) = match self.validate_game(&candidate).await? {` with `// Fetch only the challenged onchain intermediate root (not all roots).`.

2. In `crates/proof/contracts/src/aggregate_verifier.rs`, the patch replaces `/// Returns the 1-based index of the challenged intermediate root.` with `/// Returns a single intermediate output root at the given 0-based index.`.

3. In `crates/proof/contracts/src/aggregate_verifier.rs`, the patch replaces `async fn countered_index(&self, game_address: Address) -> Result<u64, ContractError> {` with `async fn intermediate_output_root(`.

4. In `crates/proof/contracts/src/aggregate_verifier.rs`, the patch adds `/// Returns the intermediate output root at the given index.`.

## Project Context

The changed code sits primarily in `crates/proof/challenge/src`, `crates/proof/challenge`, `crates/proof/contracts/src`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `crates/proof/challenge/src/submitter.rs`, `crates/proof/challenge/src/validator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/proof/challenge/src/submitter.rs`, `crates/proof/challenge/src/test_utils.rs`. The strongest project-level identifiers around this patch are `index`, `root`, `intermediate`, and `game_address`. Nearby tests or test-like files include `crates/proof/challenge/tests/driver.rs`.

## Before/After Behavior

Before the patch, `process_fraudulent_zk_challenge` started from `self.validate_game(&candidate)` and relied on broader intermediate-root validation output. The commit message says this led to a first-invalid-index heuristic, so an earlier invalid root could cause the challenger to skip nullification even when the actually challenged root was valid. After the patch, the handler fetches `intermediate_output_root(game_address, challenged_index)` and validates only that challenged checkpoint root.

# Root Cause

The challenger used validation scope that was broader than the decision boundary for this path. It considered all intermediate roots and derived the outcome from the first invalid one encountered, even though the dispute state identifies one specific challenged intermediate root index.

## Walkthrough

1. `FraudulentZkChallenge` is the path for games with a specific challenged intermediate root index.

2. Before the change, `process_fraudulent_zk_challenge` called `self.validate_game(&candidate)` and consumed broader validation output rather than a single-index result.

3. The commit message states the old decision used a first-invalid-index heuristic.

4. That heuristic could mis-handle the case where an earlier root was invalid but the challenged root was valid, causing the challenger to skip nullification.

5. The patch changes the driver to fetch `intermediate_output_root(game_address, challenged_index)` and validate only that root.

6. Supporting API changes add `intermediateOutputRoot(uint256 index)` so this path can retrieve the single disputed root directly.

7. Test changes align mocks and regression coverage with the indexed getter behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/proof/challenge/src/driver.rs | 407 | Fraudulent ZK challenge handling path; now fetches and validates only the challenged intermediate root before deciding whether to nullify |
| crates/proof/challenge/src/scanner.rs | 3 | Game-category mapping that routes challenged games into the `FraudulentZkChallenge` path |
| crates/proof/challenge/src/validator.rs | 1 | Output-root recomputation logic used to validate the challenged checkpoint root against L2 state |
| crates/proof/contracts/src/aggregate_verifier.rs | 57 | Contract interface exposing `intermediateOutputRoot(index)` for targeted on-chain root retrieval |
| crates/proof/contracts/src/aggregate_verifier.rs | 385 | Verifier client implementation for single-root fetch used by the challenger decision path |

## Code Snippets

## Snippet 1

Context: `crates/proof/challenge/src/driver.rs:412` (changes a consensus- or validator-sensitive branch)

Before
```rust
let game_address = candidate.factory.proxy;

        let (result, intermediate_roots) = match self.validate_game(&candidate).await? {
            Some(pair) => pair,
            None => return Ok(()),
        };

        // For Path 2: If the original proposal's root at the challenged index
```
After
```rust
let game_address = candidate.factory.proxy;

        // Fetch only the challenged onchain intermediate root (not all roots).
        let on_chain_root =
            self.verifier_client.intermediate_output_root(game_address, challenged_index).await?;

        // Validate only the challenged root — not all intermediate roots.
        // The checkpoint block for index `i` is:
```

## Snippet 2

Context: `crates/proof/contracts/src/aggregate_verifier.rs:188` (changes a sensitive control or state-update path)

Before
```rust
) -> Result<Vec<B256>, ContractError>;

    /// Returns the 1-based index of the challenged intermediate root.
    ///
```
After
```rust
) -> Result<Vec<B256>, ContractError>;

    /// Returns a single intermediate output root at the given 0-based index.
    async fn intermediate_output_root(
        &self,
        game_address: Address,
        index: u64,
    ) -> Result<B256, ContractError>;
```

## Snippet 3

Context: `crates/proof/contracts/src/aggregate_verifier.rs:406` (changes a sensitive control or state-update path)

Before
```rust
}

    async fn countered_index(&self, game_address: Address) -> Result<u64, ContractError> {
        let contract =
```
After
```rust
}

    async fn intermediate_output_root(
        &self,
        game_address: Address,
        index: u64,
    ) -> Result<B256, ContractError> {
        let contract =
```

## Snippet 4

Context: `crates/proof/contracts/src/aggregate_verifier.rs:57` (changes a sensitive control or state-update path)

Before
```rust
function intermediateOutputRoots() external view returns (bytes memory);

        /// Returns the 1-based index of the challenged intermediate root.
        ///
```
After
```rust
function intermediateOutputRoots() external view returns (bytes memory);

        /// Returns the intermediate output root at the given index.
        function intermediateOutputRoot(uint256 index) external view returns (bytes32);

        /// Returns the 1-based index of the challenged intermediate root.
        ///
```

# Fix Pattern

Replace collection-wide heuristic validation with targeted validation of the exact protocol-selected item.

## How It Was Fixed

The driver stopped depending on all intermediate roots for `FraudulentZkChallenge` handling and instead fetches the single on-chain root at `challenged_index`. The contracts client and interface were extended with `intermediate_output_root` / `intermediateOutputRoot(index)` to support that narrower check. Tests were updated to reflect indexed-root access and out-of-bounds behavior.

# Why It Matters

1. It fixes incorrect challenger behavior in a dispute-handling path.

2. It removes interference from unrelated earlier invalid roots when judging the challenged root.

3. It makes the implementation match the on-chain dispute index more directly.

4. The evidence still points to an off-chain logic correction, not a demonstrated on-chain vulnerability.

# Evidence Notes

Direct support comes from the replacement in `crates/proof/challenge/src/driver.rs` of `self.validate_game(&candidate)` with `self.verifier_client.intermediate_output_root(game_address, challenged_index).await?` and the nearby comment stating only the challenged root is validated. `crates/proof/contracts/src/aggregate_verifier.rs` adds the single-root getter at the trait, implementation, and Solidity interface layers. The commit message explicitly describes the prior misbehavior. What is not established by the provided evidence is a concrete exploit scenario, chain-wide impact, or an on-chain contract bug. Protocol security invariant: When handling a `FraudulentZkChallenge`, the challenger should judge the dispute using the single intermediate root identified by the on-chain challenged index, not by scanning unrelated intermediate roots and reacting to the first invalid one. Verification notes: The patch does not prove a chain-wide consensus failure or finalization bypass on its own. The evidence shows an off-chain challenger logic error; it does not show an on-chain contract vulnerability. The patch does not prove reliable remote denial of service beyond incorrect skip behavior in this service. The evidence does not show confidentiality, memory-safety, or cryptographic-break impact. The behavioral claim about the old heuristic comes primarily from the commit message, not a full before/after code listing. The evidence is strong for a correctness fix in challenger decision logic. The evidence is insufficient to confirm a security vulnerability rather than a non-security protocol-handling bug. Helper and test-file changes appear supportive rather than the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `incorrect-fraud-challenge-validation`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `blockchain-core, challenger, dispute-handling, fraud-proof`

The patch is in a security-sensitive fraud-dispute path and the commit message describes a concrete bad outcome: the challenger could skip nullifying a fraudulent ZK challenge because it looked at unrelated earlier invalid roots. The implementation change narrows validation to the single challenged root, which clearly hardens enforcement of dispute correctness. However, the supplied evidence does not prove a concrete exploit, on-chain contract vulnerability, or chain-wide impact, so this is better retained as security-hardening rather than a confirmed security-fix.

## Security Evidence

1. Commit message states the old logic could cause the challenger to skip nullifying a fraudulent ZK challenge.
2. `process_fraudulent_zk_challenge` now fetches only `intermediate_output_root(game_address, challenged_index)` instead of using all intermediate roots.
3. The driver comments explicitly say it now validates only the challenged root.
4. The contract/client API was extended with a single-index getter, aligning validation with the on-chain challenged index.

## Missing Evidence

1. No proof that an attacker could reliably trigger and benefit from this condition in practice.
2. No evidence of an on-chain contract flaw, asset loss, or consensus/finality break.
3. No full pre-patch decision code is shown beyond the commit description of the heuristic.

## Claim Boundaries

1. This supports a security-relevant hardening in off-chain challenger dispute handling.
2. It does not establish a confirmed exploitable vulnerability from the patch alone.
3. It does not prove broader impacts such as chain compromise, fund loss, or remote denial of service.
