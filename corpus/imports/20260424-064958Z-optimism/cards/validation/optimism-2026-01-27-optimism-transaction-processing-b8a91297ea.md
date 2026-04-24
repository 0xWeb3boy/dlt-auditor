# Validation Card

## Metadata

- ID: `optimism-2026-01-27-optimism-transaction-processing-b8a91297ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integer-truncation`

## What Confirmed The Issue

- op-node/p2p/discovery.go changes chain-ID comparison from .Uint64() to bigs.Uint64Strict(...), removing silent truncation in peer filtering.
- op-node/cmd/batch_decoder/main.go changes rollup-config lookup from .Uint64() to bigs.Uint64Strict(...), tightening handling of oversized chain IDs.
- The commit subject/body explicitly frame the change as an overflow fix in yParity/v handling and safer strict uint64 conversion.
- The changed files include signature-related paths (span_batch_txs.go, withdrawals/utils.go), consistent with security-sensitive chain-ID logic.

## What Could Have Invalidated It

- No diff is provided for op-node/rollup/derive/span_batch_txs.go or op-node/withdrawals/utils.go, where the signature-related fix would be shown.
- The provided excerpts do not define bigs.Uint64Strict(...) or show whether it rejects, errors, or panics on oversized values.
- The patch snippets do not prove that oversized chain IDs are attacker-controlled in production or that a concrete replay/signature vulnerability existed.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No diff is provided for op-node/rollup/derive/span_batch_txs.go or op-node/withdrawals/utils.go, where the signature-related fix would be shown.
- The provided excerpts do not define bigs.Uint64Strict(...) or show whether it rejects, errors, or panics on oversized values.
- The patch snippets do not prove that oversized chain IDs are attacker-controlled in production or that a concrete replay/signature vulnerability existed.
