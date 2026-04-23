# Validation Card

## Metadata

- ID: `go-ethereum-2018-09-20-go-ethereum-storage-d6254f827`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-choice-tie-break-hardening`

## What Confirmed The Issue

- Evidence 1: The equal-total-difficulty same-height branch changed from a random 50% reorg to local-miner-aware policy logic.
- Evidence 2: `BlockChain` and `NewBlockChain` gained an `isLocalFn` hook, showing that the tie-break now depends on local trust metadata.

## What Could Have Invalidated It

- Compensating control 1: The protocol already made same-height equal-total-difficulty competitors impossible in practice.
- Compensating control 2: The local-author preference could not influence any externally visible reorg behavior in the affected deployment.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Keep the claim at hardening unless the evidence shows an attacker can reliably force the bad tie-break.
- Caution 2: Do not call this state corruption; the proof is about canonical-selection policy, not invalid block acceptance.
