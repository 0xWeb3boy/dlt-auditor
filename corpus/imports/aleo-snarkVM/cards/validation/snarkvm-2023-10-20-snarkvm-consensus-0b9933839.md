# Validation Card

## Metadata

- ID: `snarkvm-2023-10-20-snarkvm-consensus-0b9933839`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fee-validation-reward-accounting`

## What Confirmed The Issue

- Ledger transaction checking now delegates to `VM::check_transaction` with rejected context.
- VM finalization computes confirmed priority fees before preparing reward ratifications.

## What Could Have Invalidated It

- The old ledger path called the same VM checker with equivalent context.
- Coinbase reward calculation does not depend on transaction fee totals in the affected version.

## Severity Guidance

- Expected impact band: economic_consensus_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- The local and VM checks are provably equivalent and share the same inputs.
- The fee total is recomputed from canonical transaction objects before block acceptance.
