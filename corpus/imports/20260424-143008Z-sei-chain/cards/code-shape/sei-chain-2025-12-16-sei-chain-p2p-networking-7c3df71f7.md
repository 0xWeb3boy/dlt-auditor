# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-12-16-sei-chain-p2p-networking-7c3df71f7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-peer-resource-abuse-hardening`

## Code Shape Summary

- The supported finding is mempool peer-abuse hardening, not a confirmed vulnerability fix. The patch enables CheckTx error blacklisting by default, narrows the blacklist trigger away from all non-OK ABCI CheckTx results, and adds guarded peer eviction accounting.

## Search Motifs

- Motif 1: blacklist trigger counts all non-OK CheckTx results
- Motif 2: oversized tx error class separated from ordinary invalid tx
- Motif 3: default peer blacklist flag disabled or too broad

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Narrow peer-penalty triggers to bounded abuse cases, centralize guards, and enable the safer control by default.

## False Match Warnings

- The failure code reflects user-level invalid transactions rather than peer abuse.
- Eviction would let attackers disconnect honest peers by relaying bad user txs.
