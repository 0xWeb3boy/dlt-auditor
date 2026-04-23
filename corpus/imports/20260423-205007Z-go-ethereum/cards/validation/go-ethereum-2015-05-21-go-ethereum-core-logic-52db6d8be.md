# Validation Card

## Metadata

- ID: `go-ethereum-2015-05-21-go-ethereum-core-logic-52db6d8be`
- Bug family: `authz_and_role_gates`
- Bug class: `cross-check-validation-bypass`

## What Confirmed The Issue

- Evidence 1: Commit subject names a forged blockchain with known parent attack.
- Evidence 2: Regression test describes an attacker forging block parents to point to existing hashes.

## What Could Have Invalidated It

- Compensating control 1: Keep the finding limited to downloader cross-check validation bypass by malicious or faulty peers.
- Compensating control 2: Do not claim arbitrary code execution, key compromise, fund theft, or consensus validation bypass.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Keep the finding limited to downloader cross-check validation bypass by malicious or faulty peers.
- Caution 2: Do not claim arbitrary code execution, key compromise, fund theft, or consensus validation bypass.
