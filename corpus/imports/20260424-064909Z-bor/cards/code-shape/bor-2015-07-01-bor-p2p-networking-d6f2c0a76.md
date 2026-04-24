# Code-Shape Card

## Metadata

- ID: `bor-2015-07-01-bor-p2p-networking-d6f2c0a76`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- The supplied evidence supports a likely denial-of-service fix in the downloader hash-queueing path. Before the change, fetchHashes kept signaling continuation after inserting each batch. The patch adds maxQueuedHashes and makes continuation depend on d.queue.Pending() < maxQueuedHashes, stopping further fetches when the queue is full. Root cause: The hash fetch loop lacked an explicit bound on pending queued hashes and continued requesting more peer-supplied hashes without checking whether the backlog was already too large.

## Search Motifs

- remote input controls allocation, iteration count, queue length, or cache growth without a cap
- decode or validation path panics or aborts process on malformed peer/RPC data
- request processing lacks timeout, size limit, rate limit, or early reject before expensive work

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Add an explicit queue-depth cap and gate continuation of a peer-driven fetch loop on the current pending backlog.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Availability claims need an externally triggerable path and enough cost asymmetry, crashability, or missing throttling to matter.
