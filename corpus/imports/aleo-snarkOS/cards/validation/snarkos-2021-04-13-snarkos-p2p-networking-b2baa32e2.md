# Validation Card

## Metadata

- ID: `snarkos-2021-04-13-snarkos-p2p-networking-b2baa32e2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-block-sync-state-hardening`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Use the expectation check as a control-flow guard and reset stale sync counters before registering a new mutually exclusive sync attempt.
- Root-cause evidence from the finding: The supported root cause is incomplete use of existing sync-state validation in the inbound block-sync path. The handler computed whether a Sync payload matched expected peer-book state but did not use that result to decide whether consensus should process the payload. Stale peer sync counters could also remain when beginning a new sync attempt. 1. process_incoming_messages receives an inbound network payload and dispatches by payload type. 2. For Payload::Sync, the old handler called peer_book.

## What Could Have Invalidated It

- Downstream consensus sync rejects unexpected peers.
- Peer-book state is advisory and cannot affect block insertion.

## Severity Guidance

- Expected impact band: `sync-integrity-hardening`
- Expected severity band: `medium`
- Rationale: Medium severity is appropriate when the affected boundary is reachable and the sink controls unexpected sync payload processing; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- If consensus.received_sync independently validates peer expectation, impact is reduced
- Purely local sync tests are not a peer boundary
- No issue if duplicate/unexpected payloads are idempotent
