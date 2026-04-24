# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-07-24-sei-chain-transaction-processing-9836e33a2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vulnerable-cryptographic-dependency`

## Code Shape Summary

- The grounded finding is a cryptographic dependency security update with required btcec API migration. The commit message explicitly says the btcec and x/crypto bumps fix CVE-2022-44797 and CVE-2024-45337. The supplied code evidence shows public-key parsing call sites changed from `btcec.ParsePubKey(bytes, btcec.S256())` to `btcec.

## Search Motifs

- Motif 1: btcec ParsePubKey old API usage
- Motif 2: x/crypto or btcec CVE bump
- Motif 3: public key parse sites near ante or precompile verification

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Upgrade affected crypto dependencies and migrate call sites to the patched API while preserving error handling.

## False Match Warnings

- The vulnerable function is not reachable with untrusted input.
- A patched dependency is already vendored or replaced in production builds.
