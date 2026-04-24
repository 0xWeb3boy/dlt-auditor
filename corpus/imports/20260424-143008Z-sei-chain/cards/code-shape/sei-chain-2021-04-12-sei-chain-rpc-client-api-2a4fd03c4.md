# Code-Shape Card

## Metadata

- ID: `sei-chain-2021-04-12-sei-chain-rpc-client-api-2a4fd03c4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `failed-ack-state-rollback`

## Code Shape Summary

- The patch changes IBC packet receive handling so `OnRecvPacket` runs in a cached SDK context and its application-side state changes are written only when the acknowledgement is nil/asynchronous or successful. This is well supported as a protocol state-consistency and rollback fix.

## Search Motifs

- Motif 1: callback mutates state before success acknowledgement is checked
- Motif 2: cached context write occurs unconditionally after module callback
- Motif 3: failed acknowledgement path shares state context with successful receive path

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Run callbacks in a cached context and write the cache only after the protocol success/asynchronous acknowledgement condition is known.

## False Match Warnings

- The callback is read-only or all writes occur after acknowledgement success is checked.
- A lower layer already wraps the whole receive path in a transactional context and discards failed acknowledgements.
