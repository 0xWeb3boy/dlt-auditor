# Raw Finding Summary

Source: Omni Cantina `M-6`
Title: Delays in updating the l1BridgeBalance can lead to user fund losses.
Severity: `medium`

## Normalized Summary

The report gives a timing example where a delayed 1 wei L1-to-Native message overwrites the Native mirror after a 100 ether Native-to-L1 withdrawal consumed L1 liquidity. Later Native-to-L1 withdrawal succeeds on Native and fails on L1.

## Reusable Failure Shape

One bridge direction sends delayed absolute reserve snapshots while the opposite direction consumes the same mirror as a local liquidity limit.

## Missing Property

`cross-direction-reserve-freshness`: A delayed absolute reserve snapshot must not overwrite newer local decrements or admit withdrawals against liquidity already consumed by the opposite bridge direction.

## Source Evidence

- Ground-truth findings file: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Source section: `M-6`
