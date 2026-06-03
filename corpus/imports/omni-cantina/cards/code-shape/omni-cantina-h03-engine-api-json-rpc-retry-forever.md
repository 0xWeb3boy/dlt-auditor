# Code-Shape Card

Record: `omni-cantina-h03-engine-api-json-rpc-retry-forever`
Project: `omni-network`
Source finding: `Omni Cantina H-3`

## Search Shape

Payload validation routes deterministic JSON-RPC InvalidParams errors into the same retry-forever path used for transient network failures.

## Motifs

- `retryForever`
- `pushPayload err`
- `NewPayloadV3 CallContext`
- `Invalid parameters`
- `nil BlobGasUsed`
- `nil ExcessBlobGas`
- `isUnknown status`
- `ProcessProposal hang`

## Negative Signals

- JSON-RPC InvalidParams is classified as reject, not retry.
- Local validation rejects the malformed payload before Engine API.
- Retry loop has deadline or transient-error predicate.

## Likely Fix Shape

Classify Engine API errors by type: retry only transient transport/sync failures, reject deterministic invalid payload or invalid-parameter errors, and locally validate required fork fields.
