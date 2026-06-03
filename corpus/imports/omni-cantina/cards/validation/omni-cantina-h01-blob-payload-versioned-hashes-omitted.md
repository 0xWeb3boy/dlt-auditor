# Validation Card

Record: `omni-cantina-h01-blob-payload-versioned-hashes-omitted`
Project: `omni-network`
Source finding: `Omni Cantina H-1`

## Positive Confirmation

Find a path where GetPayloadV3 can include blob hashes but MsgExecutionPayload stores only payload bytes and pushPayload always passes an empty hash list.

## Preconditions To Confirm

- Cancun is active.
- Blob transactions are admitted by geth.
- The proposal commits only ExecutionPayload.
- Validators call NewPayloadV3 with an empty versionedHashes list.

## False-Positive Cautions

- The deployment disables Cancun or filters blob transactions at all ingress paths.
- Versioned hashes are reconstructed before NewPayloadV3.
- The blob sidecar is committed and validated by consensus.

## Minimal Reproduction Or Check

Create a payload containing blob transactions and assert validator import passes the exact versioned hashes or rejects before proposal.
