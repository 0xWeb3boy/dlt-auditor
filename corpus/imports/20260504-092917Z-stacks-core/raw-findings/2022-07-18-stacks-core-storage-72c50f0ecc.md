---
case_id: case_20220718_72c50f0ecc
project: stacks-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2022-07-18
source_refs:
  - git:72c50f0eccbc8196603373258d2c864008035a00
  - "src/net/rpc.rs:954"
  - "testnet/stacks-node/src/config.rs:623"
  - "src/chainstate/stacks/miner.rs:2287"
  - "src/net/connection.rs:403"
bug_class: signature-domain-binding
impact_type:
  - signature-integrity
  - validator-integrity
confidence: medium
tags:
  - validator
  - rpc
  - signature
  - structured-hash
  - domain-separation
  - fail-closed
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes validator block proposal signing from a constant placeholder hash toward structured proposal-data signing that also takes a multiparty contract identifier, and it threads that contract through connection configuration into the RPC path. This is security-relevant cryptographic plumbing, but the provided evidence does not establish a concrete vulnerability, exploitability, or that pre-fix signatures were accepted in a dangerous context. Treat this as unclear compatibility or hardening work, not a confirmed security fix.

## Observed Patch Facts

1. In `src/net/rpc.rs`, the patch replaces `let response = match proposal.validate(chainstate, &sortdb.index_conn()) {` with `let signing_contract = match signing_contract {`.

2. In `testnet/stacks-node/src/config.rs`, the patch replaces `None => HELIUM_DEFAULT_CONNECTION_OPTIONS.clone(),` with `};`.

3. In `src/chainstate/stacks/miner.rs`, the patch replaces `pub fn sign(&self, signing_key: &Secp256k1PrivateKey) -> [u8; 65] {` with `pub fn sign(&self, signing_key: &Secp256k1PrivateKey, signing_contract: QualifiedCont...`.

4. In `src/net/connection.rs`, the patch adds `/// the contract used to submit multiparty commits (if a validator)`.

## Project Context

The changed code sits primarily in `src/net`, `testnet/stacks-node/src`, `testnet/stacks-node`, which anchors the finding in the `storage` area of the project. Historical context from `src/net/http.rs`, `src/net/server.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/net/http.rs`, `testnet/stacks-node/src/main.rs`. The strongest project-level identifiers around this patch are `contract`, `signing_key`, `HttpResponseType::BlockProposalInvalid`, and `sign`. Nearby tests or test-like files include `testnet/stacks-node/src/tests/l1_multiparty.rs`, `testnet/stacks-node/src/tests/neon_integrations.rs`.

## Before/After Behavior

Before the patch, `Proposal::sign` accepted only a validator key and the shown code signed a fixed constant hash. The validator RPC path could call `proposal.sign(validator_key)` after proposal validation without requiring a configured multiparty signing contract. After the patch, signing accepts a `QualifiedContractIdentifier`, begins constructing Clarity values from proposal fields such as block hash, withdrawal merkle root, and burn tip, and the RPC handler returns `BlockProposalInvalid` if no multiparty contract is configured. Connection options now carry `hyperchain_signing_contract`, populated from `CommitStrategy::MultiMiner`.

# Root Cause

The old implementation appears to have used a placeholder signing hash and lacked a configured contract/domain input in the RPC signing path. The evidence supports an implementation correctness gap, but not enough to prove an exploitable security flaw.

## Walkthrough

1. `handle_validate_block_proposal` receives a block proposal validation request.

2. Before the change, after validation succeeded, the handler could call `proposal.sign(validator_key)` without a signing contract argument.

3. The shown old `Proposal::sign` implementation signed a fixed constant hash rather than the proposal-specific fields shown in the patched code.

4. The patch adds `hyperchain_signing_contract` to connection options and populates it from the `MultiMiner` commit strategy.

5. The RPC handler now checks that a signing contract is configured before it proceeds to produce a signed valid response.

6. The patched signing function accepts a `QualifiedContractIdentifier` and constructs typed Clarity buffers from proposal data, indicating movement toward the real structured hash expected by the multiparty contract.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/chainstate/stacks/miner.rs | 2287 | Builds and signs the validator proposal message using structured proposal data and the signing contract instead of a constant hash. |
| src/net/rpc.rs | 954 | Rejects block proposal validation requests when the validator lacks a configured multiparty signing contract before producing a signed valid response. |
| src/net/connection.rs | 403 | Carries the optional hyperchain signing contract through network connection options. |
| testnet/stacks-node/src/config.rs | 623 | Populates the signing contract from the MultiMiner commit strategy into runtime connection options. |

## Code Snippets

## Snippet 1

Context: `src/net/rpc.rs:954` (changes signature or replay validation logic)

Before
```rust
};

        let response = match proposal.validate(chainstate, &sortdb.index_conn()) {
            Ok(_) => {
                let signature = proposal.sign(validator_key);
                HttpResponseType::BlockProposalValid {
                    metadata: response_metadata,
```
After
```rust
};

        let signing_contract = match signing_contract {
            Some(key) => key,
            None => {
                let response = HttpResponseType::BlockProposalInvalid {
                    metadata: response_metadata,
                    error_message:
```

## Snippet 2

Context: `testnet/stacks-node/src/config.rs:623` (changes a sensitive control or state-update path)

Before
```rust
hyperchain_validator: node.mining_key.clone(),
                    ..ConnectionOptions::default()
                }
            }
            None => HELIUM_DEFAULT_CONNECTION_OPTIONS.clone(),
```
After
```rust
hyperchain_validator: node.mining_key.clone(),
                    ..ConnectionOptions::default()
                };
                if let CommitStrategy::MultiMiner { ref contract, .. } = &burnchain.commit_strategy {
                    result_opts.hyperchain_signing_contract = Some(contract.clone());
                }

                result_opts
```

## Snippet 3

Context: `src/chainstate/stacks/miner.rs:2287` (changes signature or replay validation logic)

Before
```rust
/// Sign this proposal with `signing_key`, returning a serialized recoverable
    /// signature that can be validated by the multiminer contract.
    pub fn sign(&self, signing_key: &Secp256k1PrivateKey) -> [u8; 65] {
        // when using a 2.0 layer-1, must use a constant
        // when using a 2.1 layer-1, this will need to use the structured data hash
        let message_hash =
            hex_bytes("e2f4d0b1eca5f1b4eb853cd7f1c843540cfb21de8bfdaa59c504a6775cd2cfe9")
                .expect("Failed to parse hex constant");
```
After
```rust
/// Sign this proposal with `signing_key`, returning a serialized recoverable
    /// signature that can be validated by the multiminer contract.
    pub fn sign(&self, signing_key: &Secp256k1PrivateKey, signing_contract: QualifiedContractIdentifier) -> [u8; 65] {
        // when using a 2.0 layer-1, must use a constant
        // let structured_hash =
        //     hex_bytes("e2f4d0b1eca5f1b4eb853cd7f1c843540cfb21de8bfdaa59c504a6775cd2cfe9")
        //         .expect("Failed to parse hex constant");
        // when using a 2.1 layer-1, this will need to use the structured data hash
```

## Snippet 4

Context: `src/net/connection.rs:403` (changes a sensitive control or state-update path)

Before
```rust
/// hyperchain validator key
    pub hyperchain_validator: Option<Secp256k1PrivateKey>,
}
```
After
```rust
/// hyperchain validator key
    pub hyperchain_validator: Option<Secp256k1PrivateKey>,
    /// the contract used to submit multiparty commits (if a validator)
    pub hyperchain_signing_contract: Option<QualifiedContractIdentifier>,
}
```

# Fix Pattern

Thread required signing-domain configuration into the validator path, fail closed when it is absent, and derive signatures from structured proposal data instead of a constant placeholder hash.

## How It Was Fixed

The patch added a signing contract field to `ConnectionOptions`, populated it from multiminer configuration, added an RPC guard for missing contract configuration, and changed `Proposal::sign` to receive the signing contract while building structured Clarity values from proposal fields.

# Why It Matters

1. Validator signatures should be scoped to the intended proposal and contract context.

2. A constant signing hash does not express proposal-specific intent in the shown code.

3. Failing closed on missing contract configuration reduces accidental invalid or context-free signing.

4. The evidence does not prove attacker access, replay impact, consensus impact, or accepted forged signatures.

# Evidence Notes

Grounded evidence comes from `src/chainstate/stacks/miner.rs`, `src/net/rpc.rs`, `src/net/connection.rs`, and `testnet/stacks-node/src/config.rs`. The patch clearly changes signing inputs and configuration flow. However, the evidence does not show the complete final hash construction, contract verification behavior, whether old signatures were accepted, or any attacker-controlled path that turns the placeholder hash into a practical vulnerability. Protocol security invariant: Validator proposal signatures should be generated over the structured proposal data and the intended multiparty signing contract context, and the node should not emit such signatures without that context configured. Verification notes: The patch does not prove that an attacker could obtain a useful signature before the fix. The patch does not prove consensus divergence or chain state corruption. The patch does not show private key disclosure or signature forgery. The patch may also be compatibility work for real contract validation rather than a demonstrated vulnerability exploit fix. Do not classify as confirmed or likely security fix from the provided patch alone. No evidence of private key disclosure, signature forgery, replay exploit, or consensus divergence is provided. Commit subject suggests implementation compatibility with real structured hashes as much as vulnerability remediation. Keep out of the security corpus unless additional evidence shows exploitable acceptance or misuse of the old constant-hash signatures. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-domain-binding`
Final impact type: `signature-integrity, validator-integrity`
Final confidence: `medium`
Final tags: `validator, rpc, signature, structured-hash, domain-separation, fail-closed`

The evidence does not prove a concrete exploitable vulnerability, so this should not be treated as a confirmed security fix. However, the patch clearly tightens security-sensitive validator signing behavior by replacing a constant placeholder signing hash with proposal/contract-derived structured data and by failing closed when the multiparty signing contract is not configured. That supports retaining it as security hardening, with conservative metadata rather than the original storage/state-corruption framing.

## Security Evidence

1. Proposal::sign previously signed a fixed constant hash and now accepts a QualifiedContractIdentifier while constructing structured Clarity values from proposal fields.
2. The RPC validation path now refuses to emit a signed valid response when no multiparty signing contract is configured.
3. ConnectionOptions now carries hyperchain_signing_contract and config populates it from CommitStrategy::MultiMiner.
4. The changed path involves validator block proposal signatures, which are security-sensitive even absent demonstrated exploitability.

## Missing Evidence

1. No proof that the old constant-hash signatures were accepted by production contract verification.
2. No demonstrated attacker-controlled request flow that could obtain a useful signature.
3. No evidence of replay, forgery, consensus divergence, or state corruption caused by the old behavior.
4. Commit subject suggests compatibility with real structured hashes, not explicit vulnerability remediation.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. Do not claim state corruption from the supplied evidence.
3. Do not claim private key disclosure, signature forgery, or exploitable replay.
4. Validated scope is validator signature binding and fail-closed configuration behavior.
