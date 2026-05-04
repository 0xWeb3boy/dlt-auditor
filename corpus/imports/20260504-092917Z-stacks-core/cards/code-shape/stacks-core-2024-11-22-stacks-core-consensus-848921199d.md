# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-11-22-stacks-core-consensus-848921199d`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-consensus-validation-race`

## Code Shape Summary

- The patch likely fixes a security-relevant race in signer block validation. The supported claim is that queued validation approval could be applied after the signer's sortition view changed, and the fix rechecks the block against the current view before local acceptance. The evidence does not establish signature forgery, private key compromise, replay, or guaranteed final on-chain invalid block acceptance.

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
