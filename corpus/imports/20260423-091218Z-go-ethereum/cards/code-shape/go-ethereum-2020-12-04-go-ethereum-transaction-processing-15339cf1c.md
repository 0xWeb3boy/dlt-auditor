# Code-Shape Card

## Metadata

- ID: `go-ethereum-2020-12-04-go-ethereum-transaction-processing-15339cf1c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signed-vulnerability-advisory-check`

## Code Shape Summary

- A security-status checker loads external advisory documents, verifies detached signatures against trusted keys, and only then maps the authenticated advisory data onto local version ranges.

## Search Motifs

- Motif 1: Vulnerability or advisory feed fetched from file or network source.
- Motif 2: Detached signature or public-key verification added before parsing advisory contents.
- Motif 3: Version-range evaluation wired to warning or reporting paths after signature validation.

## Typical Asymmetry

- The attacker can tamper with metadata far from the node, while the defender may still trust that metadata enough to influence local security decisions.

## Patch Pattern

- Add a trust root for advisory documents and verify signatures before using feed contents to label versions or emit warnings.

## False Match Warnings

- Adding a new checker from scratch is not the same as fixing a proven exploitable spoofing bug.
- Real CVE metadata in test fixtures does not prove the same commit fixes that CVE's underlying runtime issue.
