# Code-Shape Card

## Metadata

- ID: `solana-2022-06-02-solana-cryptography-a781cff386`
- Bug family: `staking_registry_and_accountability`
- Bug class: `quic-stake-admission-control`

## Code Shape Summary

The provided evidence supports a Solana TPU/QUIC transaction-forwarding functional fix with possible resource-control hardening, not a confirmed vulnerability fix. The patch gates QUIC connection handling on nonzero stake or available unstaked-connection capacity, changes banking-stage forwarding to derive destinations from ForwardOption, handles NotForward earlier, and corrects a TPU shutdown log message. Claims about cryptography, replay protection, f...

## Search Motifs

- search for quic stake admission control checks near cryptography entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Use explicit transport admission and forwarding-state selection at the point of action: gate QUIC handling on stake or configured unstaked capacity, and derive forwarding destinations from ForwardOption rather than passing a fixed forwarding address through the banking-stage path.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
