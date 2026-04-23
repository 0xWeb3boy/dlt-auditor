# Code-Shape Card

## Metadata

- ID: `go-ethereum-2017-02-13-go-ethereum-storage-e23e86921`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-content-integrity-check`

## Code Shape Summary

- A content-addressed ingestion path trusts the advertised object key more than the recomputed digest from the received payload, allowing unverified bytes to cross into durable storage or retrieval logic.

## Search Motifs

- Motif 1: Peer store handler writes chunk data before comparing digest to key.
- Motif 2: Retrieval path detects a hash mismatch only after loading persisted bytes.
- Motif 3: Repair logic is added alongside a new digest check for incoming or persisted objects.

## Typical Asymmetry

- The attacker controls payload bytes and the claimed identifier, while the defender assumes the identifier already encodes the payload's integrity.

## Patch Pattern

- Hash the payload at ingest and retrieval boundaries, reject mismatches, and delete corrupt records through the normal indexed cleanup path.

## False Match Warnings

- Do not match systems where object IDs are not supposed to be content-derived.
- Do not treat corruption cleanup alone as the bug if payload-to-key verification already existed at the ingestion boundary.
