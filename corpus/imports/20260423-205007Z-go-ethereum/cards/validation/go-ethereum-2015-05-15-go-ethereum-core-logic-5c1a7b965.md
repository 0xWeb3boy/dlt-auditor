# Validation Card

## Metadata

- ID: `go-ethereum-2015-05-15-go-ethereum-core-logic-5c1a7b965`
- Bug family: `authz_and_role_gates`
- Bug class: `p2p-sync-validation-bypass`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says it circumvents a fake blockchain attack.
- Evidence 2: Downloader code now rejects a sampled block whose parent is not in the queued chain.

## What Could Have Invalidated It

- Compensating control 1: This supports a security fix in the eth/downloader P2P synchronization path.
- Compensating control 2: The validated issue is fake-chain or disconnected-chain acceptance during cross-checking.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: This supports a security fix in the eth/downloader P2P synchronization path.
- Caution 2: The validated issue is fake-chain or disconnected-chain acceptance during cross-checking.
