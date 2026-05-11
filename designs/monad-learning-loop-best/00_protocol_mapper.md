# Prompt: Protocol Mapper

Use this prompt first.

## Objective

Build a protocol-centered threat map of any blockchain or DLT repository before searching for vulnerabilities.

## Prompt

```text
You are auditing an unfamiliar blockchain or DLT repository. Before proposing any vulnerabilities, build a protocol map of the codebase.

Step 1: Discover the architecture.
- Read the top-level README, docs index, protocol specs, architecture docs, ADRs, whitepaper references, API docs, and consensus docs if present.
- Identify the main code directories that implement:
  - transaction admission and execution,
  - consensus or ordering,
  - storage or state commitment,
  - networking or p2p,
  - RPC or APIs,
  - validator, committee, relayer, bridge, sequencer, or operator logic,
  - staking, governance, slashing, or other economic logic,
  - cryptography, keys, attestation, or proof verification.

Step 2: Build the protocol map.

Your task:
1. List the main trust boundaries.
2. List all externally reachable, peer-reachable, operator-reachable, or governance-reachable entrypoints relevant to security.
2a. Map operator and deployment tooling separately from runtime protocol paths. For privileged chain setup, upgrades, verifier deployment, or contract registration, identify where transactions are built, signed, broadcast, reviewed, and stored. Distinguish offline construction from hot-key signing, multisig approval, and direct broadcast.
3. List the signed, authenticated, or proof-bearing artifacts and what they are supposed to bind.
3a. For each attestation-like artifact, including vote extensions, side votes, checkpoint signatures, committee approvals, bridge validator votes, and oracle reports, map:
  - who creates it,
  - which height, round, block hash, chain/domain, signer set, and voting-power snapshot it is supposed to bind,
  - where syntactic decoding happens,
  - where validator/signature/quorum validation happens,
  - where the attestation is finally counted, persisted, or used to accept a proposal/state transition.
3b. For ZK rollups or proof-based execution systems, build a field-binding matrix for each operation family:
  - user/API transaction fields,
  - SDK or wallet signed payload,
  - typed-data or raw-message domain fields,
  - witness struct fields,
  - pubdata or calldata fields,
  - circuit constraints and validity flags,
  - storage/account state consumed by execution,
  - verifier or contract inputs.
  For each field, mark which representation is authoritative and where equality, range, nonce, signer, and domain binding is enforced before proof acceptance or state commitment.
3c. For VM, proof, or circuit-backed systems, map native execution, circuit synthesis, deployment verification, fee/finalization, and rejected or aborted transaction handling as separate representations of the same protocol state. Mark which layer is authoritative for each value and where the other layers recompute, compare, or reject it before acceptance.
4. List the major lifecycle or state machines.
5. List places where policy, version, fork, or feature gates are expected.
6. List the authoritative sources of truth for policy, checkpoints, historical state, fork activation, and head/safe/finalized positions. Distinguish them from caches, local config, watch channels, mirrors, and derived summaries.
7. For each major security decision, note the observation layer and the enforcement layer. Call out any watcher, helper, builder, provider, executor, or storage-writer split.
8. List protocol facts that appear in more than one representation or channel, such as:
  - signed body vs transport metadata,
  - serialized task or block fields vs side arguments,
  - structured headers vs stored hashes or IDs,
  - proof-carried metadata vs locally selected verifier or config artifacts.
9. For each duplicated protocol fact, note:
  - which representation is authoritative,
  - where canonicalization is supposed to happen,
  - where equality or recomputation is supposed to be enforced before the sensitive sink.
10. Identify the subsystems where a missing authorization, missing signature binding, missing gas or quota charge, stale state cleanup, or unchecked arithmetic bug would be most dangerous.
11. Map long-lived peer-driven pipelines separately from one-shot handlers:
  - downloader, header sync, body sync, state sync, snapshot sync,
  - tx announcements and tx fetch,
  - discovery ping or pong and bonding,
  - query fanout or history-retrieval paths.
  For each, note:
  - pending-response tokens, nonces, or request identifiers,
  - lineage or predecessor checks that bind a response to local context,
  - progress counters or "made progress" signals,
  - queue, reservation, or fetch-capacity limits,
  - peer-penalty or bad-peer feedback hooks,
  - where metadata is validated before expensive work is scheduled.
12. Map consensus-rule validation surfaces separately from generic input validation:
  - Engine or consensus APIs,
  - block import and sidechain import,
  - forkchoice or head/safe/finalized updates,
  - payload building and payload validation,
  - chain-variant or rollup-specific validators,
  - replay, recovery, migration, and compatibility validators.
  For each surface, note which canonical validator should run and which fork, method-version, timestamp, height, chain variant, or payload-type gates define the accepted fields.
13. Map authenticated-state derivation surfaces:
  - state roots,
  - trie or accumulator proofs,
  - checkpoints,
  - pruning and compaction,
  - fork overlays,
  - state-provider caches,
  - canonical persistence handoffs.
  For each, identify what binds derived data to the canonical block, root, range, fork, or target.
14. Map read-only, debug, witness, trace, or simulation paths that reuse normal execution or import helpers.
  For each, identify:
  - whether the shared helper can still reach persistent writers, journaling, or canonical-state mutation,
  - what flag, mode, or option is supposed to disable writes,
  - whether that write suppression is enforced at the actual sink or only in a wrapper layer.
15. Map validator, prover, and runtime artifact-selection surfaces separately:
  - module root, machine version, latest alias, genesis identity, verifier config, and challenge-specified artifacts.
  For each surface, note:
  - where alias or default selection happens,
  - what measured identity the loaded artifact reports,
  - where that measured identity is compared against the expected chain, challenge, or config identity before use.
16. Map extraction, witness-recording, validation, pruning, and sequencing pipelines as one integrity boundary when the repo has delayed-message, DA, inbox, bridge, or proof-support subsystems.
  For each pipeline, note:
  - what raw inputs are extracted,
  - what witness or auxiliary data must be recorded for later validation,
  - what finalized, safe, validated, or read-progress boundary governs retention and reuse,
  - which sink consumes the recorded data to authorize sequencing, validation, or proof generation.
  For event-ingestion pipelines, also map the full source event identity:
  - source chain,
  - contract or emitter,
  - block hash and number,
  - transaction hash or index,
  - log index or event index,
  - event type,
  - payload.
  Note any progress watermark or duplicate guard and whether it is keyed by the full identity or by a coarser block, batch, height, or timestamp proxy.
17. Map internally generated follow-on work separately from user-supplied work:
  - retryables, auto-redeems, delayed messages, background challenge moves, queue-drained work, and protocol-generated side effects.
  For each, note:
  - what parent operation spawned it,
  - whether success or failure must revert the whole group,
  - whether replay, recovery, or alternate execution modes rebuild the same group with the same atomicity rules.
18. Map transaction application phases and invariant enforcement:
  - preflight, preclaim, signature and authorization checks, execution, generated side effects, invariant visit and finalize hooks, and feature or fork gates.
  For each transaction family, note:
  - which ledger, state, or protocol objects can be created, deleted, or mutated indirectly,
  - where reserves, owner counts, freeze or restriction policy, resource charges, and accounting aggregates are checked,
  - whether those checks run before the final state write and after generated side effects are known.
  For transaction admission and mempool-like systems, map committed account state separately from local pending, in-flight, reserved, or recently-used transaction state. For each sender nonce, sequence number, ticket, or replay coordinate, identify:
  - the stale lower bound,
  - the too-new upper bound,
  - duplicate guards,
  - insertion, forwarding, and execution-scheduling points,
  - cleanup, expiry, or garbage-collection policy.
18a. For every replay-sensitive coordinate such as nonce, sequence, ticket, reservation, vote freshness, or local pending state, build a lifecycle timeline across admission, fee/resource charging, execution, failure, rollback, replay, and cleanup. Identify where the coordinate is consumed or reserved, where it is reloaded from authoritative state, and which failure paths must preserve the consumed state instead of restoring the pre-admission value.
18b. For every quota, token bucket, permit, in-flight counter, archive/decompression buffer, and worker-pool budget, map query, consume/reserve, release, drop, and error paths separately. Distinguish "is allowed" checks from checks that actually consume capacity, and note whether allocation formulas use concrete input size, declared output size, configured limits, or the minimum of those bounds.
19. Map validator, committee, signer, or trust-list material by namespace:
  - long-term identity keys, ephemeral signing keys, publisher keys, manifests, revocation caches, validator lists, committee lists, trust-list publishers, quorum or threshold policy, remote fetch policy, and p2p propagation.
  For each namespace, note:
  - who is authoritative,
  - what event invalidates or rotates it,
  - which cache or mirror stores it,
  - where namespace equality is checked before accepting signed or trusted artifacts.
20. If the repository is a fork, extension, rollup adaptation, or chain-variant of a larger client, map base-client invariants separately from variant-specific invariants:
  - which transaction/header/block types are inherited unchanged,
  - which validators are shared but parameterized by variant-specific fork, timestamp, gas, sequencer, or artifact state,
  - which generated side effects or internal transactions are added by the variant,
  - which base-client caches, pools, signers, or state journals are reused by the variant,
  - where the variant's authoritative source of truth overrides or augments base-client assumptions.
  For inherited upstream features, build a variant-rule matrix:
  - upstream rule or field,
  - local feature enabled/disabled status,
  - authoritative fork coordinate,
  - expected field presence before activation,
  - expected field presence and value after activation,
  - every admission, block-building, replay, recovery, and syntactic-validation path that must enforce it.
  Treat "upstream fork support exists" as distinct from "this chain enables every upstream feature."
21. Map all cross-runtime adapter surfaces separately:
  - precompiles,
  - wasm or smart-contract query payload builders,
  - EVM-to-native message dispatch,
  - native-to-EVM receipt or accounting bridges,
  - legacy compatibility adapters.
  For each adapter, identify the canonical native path it should match, the exact identity or address-association source, the validation function or message-server path it should reuse, and the final value-transfer, governance, or accounting sink.
  For VM, native, precompile, or host-function hooks, map the active execution frame separately from decomposed caller, callee, code address, input, gas, and read-only values. Identify where direct execution is distinguished from delegated or code-substituted execution, and where the hook finally receives authoritative call-frame state.
  For every VM/native adapter, precompile, proxy bridge, or legacy compatibility path, build a caller/target class matrix:
  - EOA, smart contract, precompile, system account, proxy/delegated account, root/governance origin.
  For each class pair, identify:
  - which selectors or methods are allowed,
  - whether the target is classified by code, registry, precompile table, or native account state,
  - whether policy is enforced before selector dispatch and before the final native sink,
  - whether fee, gas, weight, proof-size, and return-data semantics match the canonical native path.
  For every VM/native adapter or precompile, also build a caller-mode matrix for direct user calls, contract calls, delegated or proxy calls, and module-originated callbacks. For each mutable method, identify where the active execution frame, caller class, read-only flag, gas budget, and native authority are checked before the native sink.
22. Map consensus-visible result data separately from state writes:
  - acknowledgements,
  - ABCI or execution result data,
  - precompile return bytes,
  - error strings,
  - receipts,
  - app-hash or results-hash inputs,
  - deterministic ordering assumptions such as map iteration.
  For each, identify whether the bytes are deterministic protocol outputs or node-local diagnostics.
23. For consensus certificates and view or round transitions, map:
  - which certificate is authoritative,
  - which locks, proposal identities, part-set headers, or latest quorum state it carries forward,
  - where verification happens,
  - where the verified certificate data is later used to mutate local state or emit votes.
24. For externally anchored or multi-chain consensus, map the base-chain or external-consensus coordinates that local validation depends on:
  - anchor block,
  - sortition,
  - epoch or reward cycle,
  - signer, validator, or committee snapshot,
  - canonical local tip,
  - fork history.
  Identify which database, contract, checkpoint source, or cache is authoritative for each coordinate and which paths use derived or memoized copies.

Output format:
- System summary
- Trust boundaries
- Entry points
- Signed/authenticated/proof artifacts
- State machines
- Version, fork, or policy gates
- High-risk files and functions
- Open questions

Constraints:
- Be concrete and repo-specific.
- Name files and functions.
- Distinguish cryptographic verification from authorization and policy enforcement.
- Distinguish admission, simulation, execution, settlement, finalization, and recovery paths where relevant.
- If the repo uses unfamiliar terminology, translate it into these generic categories.
```

Operational note: repository docs, README notes, public issue lists, or "out of scope" comments are useful metadata, but they do not by themselves kill a candidate. Record them in context, then require current code-level evidence that the exact mechanism is fixed before a later scan suppresses it.
