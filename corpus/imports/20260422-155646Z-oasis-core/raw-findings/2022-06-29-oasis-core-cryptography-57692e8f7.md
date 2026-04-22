---
case_id: case_20220629_57692e8f7
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2022-06-29
source_refs:
  - git:57692e8f7530ff20eabf458a67bf65df9e9cdf3a
  - "runtime/src/consensus/tendermint/verifier.rs:397"
  - "runtime/src/consensus/verifier.rs:49"
  - "runtime/src/consensus/tendermint/verifier.rs:724"
  - "runtime/src/consensus/tendermint/verifier.rs:667"
bug_class: missing-query-verification
impact_type:
  - query-integrity
confidence: medium
tags:
  - blockchain-core
  - consensus
  - historical-query
  - verification
  - state-integrity
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes historical-query verification from a looser or explicitly unverified accessor model to a dedicated `verify_for_query` path. The code supports a claim of improved integrity checking for query-time state access, but the provided evidence does not establish a concrete exploitable vulnerability or show impact beyond correctness/hardening of historical queries.

## Observed Patch Facts

1. In `runtime/src/consensus/tendermint/verifier.rs`, the patch replaces `fn trust(&self, cache: &mut Cache, header: ComputeResultsHeader) -> Result<(), Error> {` with `fn verify_for_query(`.

2. In `runtime/src/consensus/verifier.rs`, the patch replaces `/// Return the consensus layer state accessor for the given consensus layer block WIT...` with `/// Verify that the given runtime header is valid at the given consensus layer block...`.

3. In `runtime/src/consensus/tendermint/verifier.rs`, the patch adds `false,`.

4. In `runtime/src/consensus/tendermint/verifier.rs`, the patch replaces `Command::Trust(header, sender) => {` with `Command::Verify(consensus_block, runtime_header, epoch, sender, true) => {`.

## Project Context

The changed code sits primarily in `runtime/src/consensus/tendermint`, `runtime/src/consensus`, `runtime/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `runtime/src/consensus/roothash.rs`, `runtime/src/consensus/tendermint/store.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/types.rs`, `runtime/src/dispatcher.rs`. The strongest project-level identifiers around this patch are `Error::Internal`, `Error`, `consensus_block`, and `runtime_header`. Nearby tests or test-like files include `runtime/src/storage/mkvs/tests/mod.rs`.

## Before/After Behavior

Before the patch, the verifier trait exposed a query-related accessor documented as returning consensus state without verification, and the shown Tendermint verifier snippets did not expose a dedicated `verify_for_query` entry point. After the patch, the trait adds `verify_for_query(...)`, query-mode command dispatch routes to it, and the implementation explicitly rejects runtime headers whose namespace does not match the trusted runtime ID before returning consensus state.

# Root Cause

Historical-query handling did not have a clearly enforced verification step in the shown interface/dispatch path, so query consumers could rely on weaker validation than the normal verifier path. The evidence supports missing or insufficient query-time binding checks, not stronger claims such as signature bypass or replay exploitation.

## Walkthrough

1. `runtime/src/consensus/verifier.rs` replaces a query-related contract described as returning consensus state without verification with a new `verify_for_query(...)` API documented as performing verification for queries.

2. `runtime/src/consensus/tendermint/verifier.rs` adds a dedicated `verify_for_query` implementation in the verifier.

3. That implementation explicitly checks `runtime_header.namespace` against `self.trust_root.runtime_id` and fails on mismatch.

4. The public verifier handle adds a separate `verify_for_query(consensus_block, runtime_header, epoch)` method.

5. Verifier command dispatch distinguishes normal verification from query verification and routes query mode through `self.verify_for_query(...)`.

6. The surrounding context shows verified state roots and verification metadata being updated on successful verification, indicating the patch ties query-time state access to an explicit verification path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/consensus/verifier.rs | 49 | Trait contract changed from unverified consensus-state access to verified query-time access |
| runtime/src/consensus/tendermint/verifier.rs | 397 | Historical-query verifier implementation validates runtime header binding before returning consensus state |
| runtime/src/consensus/tendermint/verifier.rs | 667 | Verifier command dispatch sends query mode through the dedicated verification path |
| runtime/src/consensus/tendermint/verifier.rs | 724 | Public verifier handle exposes separate query verification entry point |

## Code Snippets

## Snippet 1

Context: `runtime/src/consensus/tendermint/verifier.rs:397` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    fn trust(&self, cache: &mut Cache, header: ComputeResultsHeader) -> Result<(), Error> {
        if let Some(state_root) = header.state_root {
```
After
```rust
}

    fn verify_for_query(
        &self,
        cache: &mut Cache,
        instance: &mut Instance,
        consensus_block: LightBlock,
        runtime_header: Header,
```

## Snippet 2

Context: `runtime/src/consensus/verifier.rs:49` (changes a consensus- or validator-sensitive branch)

Before
```rust
) -> Result<ConsensusState, Error>;

    /// Return the consensus layer state accessor for the given consensus layer block WITHOUT
    /// performing any verification. This method should only be used for operations that do not
```
After
```rust
) -> Result<ConsensusState, Error>;

    /// Verify that the given runtime header is valid at the given consensus layer block and return
    /// the consensus layer state accessor for that block.
    ///
    /// This is a relaxed version of the `verify` function that should be used for verifying state
    /// in queries.
    fn verify_for_query(
```

## Snippet 3

Context: `runtime/src/consensus/tendermint/verifier.rs:724` (changes signature or replay validation logic)

Before
```rust
epoch,
                sender,
            ))
            .map_err(|_| Error::Internal)?;
```
After
```rust
epoch,
                sender,
                false,
            ))
            .map_err(|_| Error::Internal)?;

        receiver.recv().map_err(|_| Error::Internal)?
    }
```

## Snippet 4

Context: `runtime/src/consensus/tendermint/verifier.rs:667` (changes signature or replay validation logic)

Before
```rust
.map_err(|_| Error::Internal)?;
                }
                Command::Trust(header, sender) => {
                    sender
```
After
```rust
.map_err(|_| Error::Internal)?;
                }
                Command::Verify(consensus_block, runtime_header, epoch, sender, true) => {
                    sender
                        .send(self.verify_for_query(
                            &mut cache,
                            &mut instance,
                            consensus_block,
```

# Fix Pattern

Introduce a dedicated verification API for read-only historical queries and enforce minimal identity/binding checks before returning consensus state.

## How It Was Fixed

The fix adds `verify_for_query` to the verifier trait, implements it in the Tendermint verifier, routes query-mode requests through that path, and adds an explicit runtime-ID/namespace check before query-time consensus state is returned or treated as verified.

# Why It Matters

1. Historical queries should not rely on unverified consensus-state access.

2. The added namespace check prevents accepting a header for the wrong runtime on the query path.

3. The patch improves integrity of query-time state handling and related verification caches.

4. The evidence does not show write-path impact or a demonstrated attacker-controlled exploit.

# Evidence Notes

The strongest direct evidence is the trait change in `runtime/src/consensus/verifier.rs`, the new `verify_for_query` implementation and namespace check in `runtime/src/consensus/tendermint/verifier.rs`, and the query-mode dispatch that now calls the dedicated verifier. The record supports an insufficient-verification/correctness-hardening interpretation. It does not directly prove signature forgery, replay, cross-runtime disclosure, or state-transition compromise. Protocol security invariant: Historical query state access should only use consensus state derived from a runtime header that has been checked against the expected runtime identity and associated consensus block. Verification notes: The patch does not prove an attacker could forge or bypass Tendermint light-client signatures. The patch does not show a write-path or state-transition exploit; the visible impact is on historical query validation. The patch does not prove confidentiality impact or cross-runtime data disclosure. The exact exploitability depends on higher-level exposure of historical query inputs, which is not shown in the provided evidence. The provided snippets show the new query-verification path and one explicit runtime-ID check. The old call sites for the previously documented unverified accessor are not shown. No exploit scenario, attacker input path, or security impact beyond query integrity is demonstrated in the provided evidence. Security relevance is plausible, but not established strongly enough to keep as a confirmed or likely vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-query-verification`
Final impact type: `query-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, historical-query, verification, state-integrity`

The patch directly hardens a security-sensitive consensus verification path for historical queries. The supplied evidence shows that query-time state access previously relied on an explicitly unverified accessor and is changed to a dedicated `verify_for_query` path that validates the runtime header against the trusted runtime ID and routes query requests through verification. That supports keeping this as a security-hardening case focused on query/state integrity. The evidence does not, however, prove a concrete exploitable vulnerability such as signature forgery, replay, data disclosure, or write-path compromise, so it should not be retained as a full security-fix finding.

## Security Evidence

1. The verifier trait documentation changes from returning consensus state "WITHOUT performing any verification" to a `verify_for_query` API for queries.
2. A dedicated `verify_for_query` implementation is added in the Tendermint verifier for historical-query handling.
3. The new query verification path explicitly rejects headers whose `runtime_header.namespace` does not match the trusted runtime ID.
4. Command dispatch is changed so query-mode verification flows through `verify_for_query` instead of the older trust/unverified path.
5. The public verifier handle now exposes a separate query-verification entry point, indicating explicit validation for this read path.

## Missing Evidence

1. No attacker-controlled input path or exposed RPC/query surface is shown in the provided patch evidence.
2. No proof-of-exploit, failing regression, or concrete before/after abuse case is included.
3. No evidence shows signature bypass, replay of authenticated messages, or compromise of Tendermint light-client checks.
4. No evidence shows confidentiality impact, cross-runtime data exposure, or write/state-transition impact.

## Claim Boundaries

1. Supported claim: historical-query state access was tightened from an unverified or weaker path to an explicit verification path.
2. Supported claim: the patch adds runtime-ID/namespace binding checks for query-time header validation.
3. Not supported: a concrete signature-validation bypass or replay vulnerability was fixed.
4. Not supported: attacker-triggerable cross-runtime disclosure, state corruption, or consensus compromise is demonstrated by the patch alone.
