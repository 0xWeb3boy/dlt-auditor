# Validation Card

## Metadata

- ID: `bor-2015-07-01-bor-p2p-networking-d6f2c0a76`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- Commit subject explicitly says it fixes a DOS vulnerability in hash queueing.
- A new maxQueuedHashes limit is added with the comment DOS protection.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- The diff does not show the exact resource exhausted, such as memory or CPU.
- The patch alone does not prove a complete end-to-end denial of service against a node.
