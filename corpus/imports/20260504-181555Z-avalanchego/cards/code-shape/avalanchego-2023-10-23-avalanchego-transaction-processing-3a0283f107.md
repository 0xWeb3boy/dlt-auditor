# Code-Shape Card

## Metadata

- ID: `avalanchego-2023-10-23-avalanchego-transaction-processing-3a0283f107`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-resource-validation`

## Code Shape Summary

- Transaction verification and size/gas checks were moved into the shared non-forced mempool admission path. The reusable shape is a mempool helper where forced internal insertion is allowed but all peer-facing insertions must validate resources first.

## Search Motifs

- addTx gains a force or local bypass parameter
- verifyTxAtTip adds signed-size and gas checks
- rejected remote transaction cache added to avoid repeated processing

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Centralize non-forced mempool admission checks and keep explicit trusted bypasses separate and visible.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- Forced insertion paths may intentionally bypass checks for trusted local recovery
- Do not flag duplicate validation if an earlier mandatory layer rejects all invalid remote txs
- Caching rejected txs is support evidence, not the root cause
