# Code-Shape Card

## Metadata

- ID: `go-ethereum-2015-05-21-go-ethereum-core-logic-52db6d8be`
- Bug family: `authz_and_role_gates`
- Bug class: `cross-check-validation-bypass`

## Code Shape Summary

- The downloader used queue membership as a proxy for validating the parent-child relationship of a cross-checked block. Because the expected parent was not retained in the cross-check state, a malicious peer could craft parent links to known hashes and pass the weaker check.

## Search Motifs

- Motif 1: p2p message missing exact checks for cross check validation bypass
- Motif 2: security-sensitive path reaches consensus-visible state transition or journal replay before rejecting malformed or unauthorized input
- Motif 3: Store the exact validation predicate needed for later checks, then compare peer-supplied data against that expected value instead of using approximate membership tests

## Typical Asymmetry

- A remote peer or spoofed sender can trigger more local work, state change, or outbound traffic than the cost of the crafted message.

## Patch Pattern

- Store the exact validation predicate needed for later checks, then compare peer-supplied data against that expected value instead of using approximate membership tests.

## False Match Warnings

- Keep the finding limited to downloader cross-check validation bypass by malicious or faulty peers.
- Do not claim arbitrary code execution, key compromise, fund theft, or consensus validation bypass.
