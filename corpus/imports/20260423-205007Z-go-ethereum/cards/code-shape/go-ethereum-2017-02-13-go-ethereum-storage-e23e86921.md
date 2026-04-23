# Code-Shape Card

## Metadata

- ID: `go-ethereum-2017-02-13-go-ethereum-storage-e23e86921`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-content-integrity-check`

## Code Shape Summary

- The supported root cause is incomplete enforcement of the content-addressed chunk invariant in Swarm chunk handling. Peer-supplied chunk bytes were not shown to be validated against their advertised key before use in the affected handler, and corrupt persisted records were not cleaned up consistently.

## Search Motifs

- Motif 1: p2p message missing exact checks for missing content integrity check
- Motif 2: security-sensitive path reaches consensus-visible state transition or journal replay before rejecting malformed or unauthorized input
- Motif 3: Validate content-addressed data at ingestion and cleanup boundaries, rejecting mismatched payloads and deleting corrupt records through the store's normal deletion abstraction

## Typical Asymmetry

- A remote peer or spoofed sender can trigger more local work, state change, or outbound traffic than the cost of the crafted message.

## Patch Pattern

- Validate content-addressed data at ingestion and cleanup boundaries, rejecting mismatched payloads and deleting corrupt records through the store's normal deletion abstraction.

## False Match Warnings

- Validated only as Swarm chunk integrity hardening, not as a proven high-impact vulnerability fix.
- Do not claim transaction validation, consensus safety, or Ethereum core protocol impact.
