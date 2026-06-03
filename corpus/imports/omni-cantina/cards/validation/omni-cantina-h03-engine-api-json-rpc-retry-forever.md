# Validation Card

Record: `omni-cantina-h03-engine-api-json-rpc-retry-forever`
Project: `omni-network`
Source finding: `Omni Cantina H-3`

## Positive Confirmation

Confirm NewPayloadV3 JSON-RPC errors become pushPayload errors and proposal_server retries all errors without a reject path.

## Preconditions To Confirm

- pushPayload returns a Go error for JSON-RPC errors.
- ProcessProposal retries all pushPayload errors forever.
- Local parseAndVerifyProposedPayload misses the malformed field or condition.

## False-Positive Cautions

- The malformed payload is rejected by local validation before RPC.
- Engine API invalid-parameter errors return invalid status rather than error on the reviewed client.
- The retry loop has a bounded timeout that leads to proposal rejection.

## Minimal Reproduction Or Check

Craft a payload missing required Cancun fields, observe Engine API InvalidParams, and assert fixed ProcessProposal rejects rather than loops.
