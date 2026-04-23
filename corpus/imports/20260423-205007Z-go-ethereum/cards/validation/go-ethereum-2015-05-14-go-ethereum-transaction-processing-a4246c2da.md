# Validation Card

## Metadata

- ID: `go-ethereum-2015-05-14-go-ethereum-transaction-processing-a4246c2da`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unknown-parent-sync-hardening`

## What Confirmed The Issue

- Evidence 1: Commit subject says it handles a potential unknown parent attack.
- Evidence 2: TakeBlocks changed from returning only blocks to returning blocks plus an error.

## What Could Have Invalidated It

- Compensating control 1: Classify as block downloader synchronization hardening, not transaction processing.
- Compensating control 2: Do not claim confirmed remote DoS from the supplied patch alone.

## Severity Guidance

- Expected impact band: low
- Expected severity band: low

## False-Positive Cautions

- Caution 1: Classify as block downloader synchronization hardening, not transaction processing.
- Caution 2: Do not claim confirmed remote DoS from the supplied patch alone.
