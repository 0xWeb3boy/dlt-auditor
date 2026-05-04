# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-11-26-stacks-core-consensus-d6bffcffb3`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-state-validation`

## Code Shape Summary

- The patch changes signer post-validation behavior so a successful block validation response is rechecked against current signer DB state, using a new helper that selects the highest locally or globally accepted signer block. This is plausibly consensus-relevant correctness or hardening work, but the provided evidence does not prove a concrete vulnerability, exploit path, or security impact.

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
