# Nibiru C4 MR-M-01: PREVRANDAO gives validators more bias than 1 bit per block

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2025-01-mr-m01-prevrandao-proposer-bias`

---

## `PREVRANDAO` gives validators more bias than 1 bit per block

### Original Issue
[Additional QA](https://github.com/code-423n4/2024-11-nibiru-findings/issues/51)

### Lines of Code

[`x/evm/keeper/msg_server.go`](https://github.com/NibiruChain/nibiru/blob/13c71a70c5a730060b7b096b6509b04d64c73edf/x/evm/keeper/msg_server.go#L113)

### Severity: Medium

- Impact: Medium
- Likelihood: Medium

### Description

The change effectively implements a `PREVRANDAO` non-zero provider.

It is, however, worth mentioning that the provided implementation:

```go
	pseudoRandomBytes := make([]byte, 8)
	binary.BigEndian.PutUint64(pseudoRandomBytes, uint64(ctx.BlockHeader().Time.UnixNano()))
	pseudoRandom := crypto.Keccak256Hash(append(pseudoRandomBytes, ctx.BlockHeader().LastCommitHash...))
```

Gives block proposers much more bias power than the "1-bit per block" that the Ethereum implementation has (see `Biasability` section in [EIP-4399](https://eips.ethereum.org/EIPS/eip-4399)), because `Time.UnixNano()` is something that the block proposer can influence to a much greater extent, and potentially even mine in a reasonable timeframe to obtain an acceptable pseudo-random result.

### Recommendation

While a fix for this may not be straightforward (Ethereum grabs its mix from the consensus layer), it's a weakness that can (and should?) be documented. It wouldn't be shocking if the previous "always zero" behavior is kept, as many chains, like [ZkSync](https://docs.zksync.io/zksync-protocol/differences/evm-instructions#difficulty-prevrandao) and [EVMOS](https://github.com/evmos/evmos/blob/392b2279dafa5182b3a5299f165a2e035d031e0a/x/evm/keeper/state_transition.go#L31-L52), have it hardcoded.

### Nibiru
> Acknowledged.

***
