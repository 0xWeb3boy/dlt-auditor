# Validation Card

## Metadata

- ID: `optimism-2022-09-08-optimism-transaction-processing-1c787aa01d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- BuildBlocksValidator validates untrusted pubsub/gossip messages on the P2P path.
- A new minGossipSize = 66 check rejects undersized decoded messages before the code splits data[:65] and data[65:].
- Signature recovery and sequencer-address validation were moved before further unmarshaling/handling of the payload.
- The validator now rejects invalid signatures immediately with pubsub.ValidationReject.

## What Could Have Invalidated It

- No reproducer or test is shown demonstrating the exact pre-patch runtime failure or exploitability.
- The evidence does not prove forged signatures were previously accepted.
- The patch does not show concrete consensus impact, privilege gain, or a confirmed remote crash path.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: signature-or-domain-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No reproducer or test is shown demonstrating the exact pre-patch runtime failure or exploitability.
- The evidence does not prove forged signatures were previously accepted.
- The patch does not show concrete consensus impact, privilege gain, or a confirmed remote crash path.
