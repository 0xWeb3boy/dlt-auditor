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
6. Identify the subsystems where a missing authorization, missing signature binding, missing gas or quota charge, stale state cleanup, or unchecked arithmetic bug would be most dangerous.

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
