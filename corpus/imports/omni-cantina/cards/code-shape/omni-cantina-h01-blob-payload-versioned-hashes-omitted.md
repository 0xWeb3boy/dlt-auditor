# Code-Shape Card

Record: `omni-cantina-h01-blob-payload-versioned-hashes-omitted`
Project: `omni-network`
Source finding: `Omni Cantina H-1`

## Search Shape

Engine API V3 returns payload plus blob side data, but consensus serializes only the payload and validators replay it with an empty versioned-hash argument.

## Motifs

- `GetPayloadV3 ExecutionPayloadEnvelope`
- `BlobsBundle`
- `MsgExecutionPayload execution_payload`
- `NewPayloadV3`
- `emptyVersionHashes`
- `BlobHashes`
- `CancunTime`

## Negative Signals

- Blob transactions are rejected before payload construction.
- Validators derive versioned hashes from payload transactions before NewPayloadV3.
- Consensus commits the blob bundle or equivalent sidecar.

## Likely Fix Shape

Reject blob transactions/payloads until supported, or derive and pass the payload transaction BlobHashes to NewPayloadV3; commit blob availability data if needed.
