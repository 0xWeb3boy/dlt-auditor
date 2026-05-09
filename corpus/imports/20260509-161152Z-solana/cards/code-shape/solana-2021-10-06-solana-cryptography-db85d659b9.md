# Code-Shape Card

## Metadata

- ID: `solana-2021-10-06-solana-cryptography-db85d659b9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting-hardening`

## Code Shape Summary

The patch is a broad Solana cost-model rollout across banking, replay, runtime execution, blockstore persistence, and tooling. It appears to add resource accounting and block/transaction cost limits, with some security-relevant motivation, but the supplied evidence does not prove that it fixes a specific vulnerability.

## Search Motifs

- search for resource accounting hardening checks near cryptography entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Introduce resource accounting and bounded metadata: estimate transaction costs, track accumulated block costs, reject or defer over-limit work, bound learned program-cost data, and persist cost data across restart.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
