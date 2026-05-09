# Code-Shape Card

## Metadata

- ID: `solana-2020-02-07-solana-staking-fa00803fbf`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `gossip-freshness-validation`

## Code Shape Summary

The patch adds freshness validation for CrdsValue entries received through gossip pull responses before inserting them into CRDS. It also threads stake/epoch-aware timeout data into packet handling and makes related push-message timeout arithmetic overflow-aware. This is plausibly security relevant because the data is peer-supplied gossip input, but the provided evidence does not prove a vulnerability impact beyond stale or future-timestamped values rea...

## Search Motifs

- search for gossip freshness validation checks near staking entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Validate peer-supplied gossip state before inserting it into shared local state, using overflow-aware timestamp arithmetic and policy-specific timeout exceptions.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
