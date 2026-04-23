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
3. List the signed, authenticated, or proof-bearing artifacts and what they are supposed to bind.
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
