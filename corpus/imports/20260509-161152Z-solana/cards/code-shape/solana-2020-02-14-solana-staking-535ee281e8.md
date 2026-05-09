# Code-Shape Card

## Metadata

- ID: `solana-2020-02-14-solana-staking-535ee281e8`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `peer-gossip-freshness-validation`

## Code Shape Summary

The patch adds explicit stale and future wallclock filtering for CRDS gossip pull responses before insertion into CRDS, threads stake/epoch-derived timeout data into packet handling, and changes a push timeout check to use checked_add. This is plausibly security relevant because gossip data is peer supplied, but the provided evidence does not establish a concrete vulnerability, exploit path, consensus impact, or direct safety failure.

## Search Motifs

- search for peer gossip freshness validation checks near staking entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Validate peer-supplied gossip records at the ingestion boundary before updating shared CRDS state, and use checked arithmetic for timeout comparisons where changed.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
