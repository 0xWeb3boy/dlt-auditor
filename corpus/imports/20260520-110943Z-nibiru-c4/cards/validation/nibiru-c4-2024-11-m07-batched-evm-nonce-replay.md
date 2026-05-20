# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-m07-batched-evm-nonce-replay`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `batched-evm-nonce-regression`

## What Confirmed The Issue

- Public C4 report section M-07 rated this as Medium.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if batching MsgEthereumTx is impossible.
- No issue if normal calls set nonce to msg.Nonce()+1 after execution.

## Severity Guidance

- Expected impact band: nonce replay window
- Expected severity band: medium

## False-Positive Cautions

- No issue if batching MsgEthereumTx is impossible.
- No issue if normal calls set nonce to msg.Nonce()+1 after execution.
- No issue if ante and execution both enforce final monotonic sequence.
