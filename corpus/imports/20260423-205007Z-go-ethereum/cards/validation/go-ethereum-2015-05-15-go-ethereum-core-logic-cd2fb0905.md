# Validation Card

## Metadata

- ID: `go-ethereum-2015-05-15-go-ethereum-core-logic-cd2fb0905`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-sync-no-progress-dos`

## What Confirmed The Issue

- Evidence 1: Commit subject says "prevent hash repeater attack".
- Evidence 2: Downloader now checks the number of newly inserted hashes from a peer response.

## What Could Have Invalidated It

- Compensating control 1: Supported claim is limited to peer-driven duplicate-hash replay/no-progress behavior during sync.
- Compensating control 2: Supported impact is denial-of-service or sync disruption, not chain integrity compromise.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Supported claim is limited to peer-driven duplicate-hash replay/no-progress behavior during sync.
- Caution 2: Supported impact is denial-of-service or sync disruption, not chain integrity compromise.
