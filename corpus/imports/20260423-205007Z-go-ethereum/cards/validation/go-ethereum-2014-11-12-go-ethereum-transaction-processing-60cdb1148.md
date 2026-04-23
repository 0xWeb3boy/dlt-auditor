# Validation Card

## Metadata

- ID: `go-ethereum-2014-11-12-go-ethereum-transaction-processing-60cdb1148`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-commitment-validation`

## What Confirmed The Issue

- Evidence 1: ProcessWithParent previously had the DeriveSha(block.transactions) versus block.TxSha check inside a block comment.
- Evidence 2: After the patch, the same check is active and returns an error on mismatch.

## What Could Have Invalidated It

- Compensating control 1: Supported claim: this patch tightens block transaction-root validation in a consensus-sensitive path.
- Compensating control 2: Supported claim: trie root canonicalization is commitment-calculation hygiene.

## Severity Guidance

- Expected impact band: high
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Supported claim: this patch tightens block transaction-root validation in a consensus-sensitive path.
- Caution 2: Supported claim: trie root canonicalization is commitment-calculation hygiene.
