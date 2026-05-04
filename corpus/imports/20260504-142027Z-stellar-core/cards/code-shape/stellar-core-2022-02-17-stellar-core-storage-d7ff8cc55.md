# Code-Shape Card

## Metadata

- ID: `stellar-core-2022-02-17-stellar-core-storage-d7ff8cc55`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-overlay-flow-control-hardening`

## Code Shape Summary

- Overlay read and send paths lacked explicit capacity gates and protocol-version checks around SEND_MORE and flood-message flow control.

## Search Motifs

- readBodyHandler continues without hasReadingCapacity
- SEND_MORE accepted from unsupported peer
- flood message sent before flow control capacity
- peer throttled flag added to read loop

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Add capacity checks to inbound read loops, reject unsupported flow-control messages, and gate outbound flood traffic on established flow-control state.

## False Match Warnings

- Backpressure implemented below the peer layer may mitigate read-loop issues.
- Flow-control metrics alone are not enforcement.
- Trusted-only control messages may reduce attacker reachability.
