# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-03-12-stacks-core-storage-481b01c536`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `cross-cycle-stale-state`

## Code Shape Summary

- The patch likely fixes a security-relevant stale-state issue in the signer database. It changes block storage, lookup, and removal from being keyed only by signer_signature_hash to being scoped by reward_cycle plus signer_signature_hash. The commit message explicitly says this prevents signers from acting on blocks from the previous cycle. The evidence supports a cross-cycle stale-state fix, but not a stronger claim about exploitability, fund loss, or consensus failure.

## Search Motifs

- Motif 1: cache key omits fork, epoch, reward cycle, or block height
- Motif 2: validation reads signer or consensus data from a previous cycle
- Motif 3: background validation races with changing chain tip

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Key cached or persisted state by canonical context and refresh, expire, or reject stale entries before validation.

## False Match Warnings

- The stale value may be advisory and rechecked before commit.
- Single-node local caches may be invalidated by broader lifecycle hooks not visible in the hunk.
