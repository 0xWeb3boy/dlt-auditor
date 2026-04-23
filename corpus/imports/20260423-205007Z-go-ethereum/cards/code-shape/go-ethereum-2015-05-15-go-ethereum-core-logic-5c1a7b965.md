# Code-Shape Card

## Metadata

- ID: `go-ethereum-2015-05-15-go-ethereum-core-logic-5c1a7b965`
- Bug family: `authz_and_role_gates`
- Bug class: `p2p-sync-validation-bypass`

## Code Shape Summary

- The cross-check path treated a returned block hash match as sufficient and cleared the pending check without confirming that the returned block's parent belonged to the downloader's queued hash chain.

## Search Motifs

- Motif 1: p2p message missing exact checks for p2p sync validation bypass
- Motif 2: security-sensitive path reaches bounded work queue, fetch scheduling, or peer-driven validation/import logic before rejecting malformed or unauthorized input
- Motif 3: Strengthen protocol cross-check validation by requiring structural parent linkage before accepting and clearing a sampled block check

## Typical Asymmetry

- A remote peer or spoofed sender can trigger more local work, state change, or outbound traffic than the cost of the crafted message.

## Patch Pattern

- Strengthen protocol cross-check validation by requiring structural parent linkage before accepting and clearing a sampled block check.

## False Match Warnings

- This supports a security fix in the eth/downloader P2P synchronization path.
- The validated issue is fake-chain or disconnected-chain acceptance during cross-checking.
