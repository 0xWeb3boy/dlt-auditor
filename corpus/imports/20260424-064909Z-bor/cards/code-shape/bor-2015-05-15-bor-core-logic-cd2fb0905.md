# Code-Shape Card

## Metadata

- ID: `bor-2015-05-15-bor-core-logic-cd2fb0905`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- The patch adds an explicit progress check to the peer-driven hash download loop. Before the change, the downloader would continue querying a peer even when a non-final response added no new hashes to the queue. After the change, such a zero-progress response is treated as ErrBadPeer, and the synchronisation layer removes that peer. This supports a peer-triggered denial-of-service or resource-exhaustion fix in the downloader path. Root cause: The downloader accepted non-terminal hash responses without validating that they advanced local queue state. Because the queue insertion API did not report whether anything new was added, the caller could stay in a request/response loop with a peer that kept sending duplicate hashes.

## Search Motifs

- remote input controls allocation, iteration count, queue length, or cache growth without a cap
- decode or validation path panics or aborts process on malformed peer/RPC data
- request processing lacks timeout, size limit, rate limit, or early reject before expensive work

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Expose whether untrusted input made forward progress, reject zero-progress non-terminal responses, and propagate that failure into peer removal.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
