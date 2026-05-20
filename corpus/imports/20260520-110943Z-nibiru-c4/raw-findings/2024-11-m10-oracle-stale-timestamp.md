# Nibiru C4 M-10: IOracle.queryExchangeRate returns incorrect blockTimeMs

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2024-11-m10-oracle-stale-timestamp`

---

## [[M-10] `IOracle.queryExchangeRate` returns incorrect `blockTimeMs`](https://github.com/code-423n4/2024-11-nibiru-findings/issues/2)
*Submitted by [3docSec](https://github.com/code-423n4/2024-11-nibiru-findings/issues/2)*

The `IOracle.queryExchangeRate` offers the following lookup functionality, in analogy to other oracles like Chainlinks':

```solidity
    /// @notice Queries the dated exchange rate for a given pair
    /// @param pair The asset pair to query. For example, "ubtc:uusd" is the
    /// USD price of BTC and "unibi:uusd" is the USD price of NIBI.
    /// @return price The exchange rate for the given pair
    /// @return blockTimeMs The block time in milliseconds when the price was
    /// last updated
    /// @return blockHeight The block height when the price was last updated
    /// @dev This function is view-only and does not modify state.
    function queryExchangeRate(
        string memory pair
    ) external view returns (uint256 price, uint64 blockTimeMs, uint64 blockHeight);
```

If we focus on the `blockTimeMs` returned value, this is meant to correspond to the time when the price was last updated and, in analogy to how Chainlink oracles are typically used, is most likely to be used in staleness checks.

If we see how this is implemented, we see that values are passed through from OracleKeeper (L92):

```go
File: oracle.go
78: func (p precompileOracle) queryExchangeRate(
79: 	ctx sdk.Context,
80: 	method *gethabi.Method,
81: 	args []any,
82: ) (bz []byte, err error) {
83: 	pair, err := p.parseQueryExchangeRateArgs(args)
84: 	if err != nil {
85: 		return nil, err
86: 	}
87: 	assetPair, err := asset.TryNewPair(pair)
88: 	if err != nil {
89: 		return nil, err
90: 	}
91: 
92: 	price, blockTime, blockHeight, err := p.oracleKeeper.GetDatedExchangeRate(ctx, assetPair)
93: 	if err != nil {
94: 		return nil, err
95: 	}
96: 
97: 	return method.Outputs.Pack(price.BigInt(), uint64(blockTime), blockHeight)
98: }
```

However, the `blockTime` returned by `oracleKeeper.GetDatedExchangeRate` corresponds to the "current" block time and, therefore, does not correspond to what should be returned by the precompile, that is the block time of the last price update.

The impact of this misalignment is quite severe because since the returned value is the timestamp returned is always that of the current block, the price will always look as freshly set when validated against `blockTime`, which is the most common validation. Consequently, downstream contracts will likely always pass staleness checks on potentially extremely old prices.

### Proof of Concept

A simple coded PoC for this issue consists of updating the `TestOracle_HappyPath` test in `x/evm/precompile/oracle_test.go` to simulate a precompile call at a later block than that of the price update.

Changing L66 as follows will cause the test to fail:

```go
File: x/evm/precompile/oracle_test.go
57: func (s *OracleSuite) TestOracle_HappyPath() {
58: 	deps := evmtest.NewTestDeps()
59: 
60: 	s.T().Log("Query exchange rate")
61: 	{
62: 		deps.Ctx = deps.Ctx.WithBlockTime(time.Unix(69, 420)).WithBlockHeight(69)
63: 		deps.App.OracleKeeper.SetPrice(deps.Ctx, "unibi:uusd", sdk.MustNewDecFromStr("0.067"))
64: 
65: 		resp, err := deps.EvmKeeper.CallContract(
66: 			deps.Ctx.WithBlockTime(deps.Ctx.BlockTime().Add(10*time.Second)), //  @audit query 10 seconds later
67: 			embeds.SmartContract_Oracle.ABI,
68: 			deps.Sender.EthAddr,
69: 			&precompile.PrecompileAddr_Oracle,
70: 			false,
71: 			OracleGasLimitQuery,
72: 			"queryExchangeRate",
73: 			"unibi:uusd",
74: 		)
75: 		s.NoError(err)
76: 
77: 		// Check the response
78: 		out, err := embeds.SmartContract_Oracle.ABI.Unpack(string(precompile.OracleMethod_queryExchangeRate), resp.Ret)
79: 		s.NoError(err)
80: 
81: 		// Check the response
82: 		s.Equal(out[0].(*big.Int), big.NewInt(67000000000000000))
83: 		s.Equal(out[1].(uint64), uint64(69000))
84: 		s.Equal(out[2].(uint64), uint64(69))
85: 	}
86: }
```

### Recommended Mitigation Steps

Consider maintaining and querying a lookup table (height to time) for returning the right `blockTime` instead of relying on the value passed by `GetDatedExchangeRate`.

**[Unique-Divine (Nibiru) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/2#issuecomment-2500182001):**
 > Running the steps to reproduce the issue and see if the direct context modifier works or if a CometBFT query is needed.

**[Unique-Divine (Nibiru) confirmed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/2#issuecomment-2500748003):**
 > This ticket has been addressed [here](https://github.com/NibiruChain/nibiru/pull/2117). This change adds the block timestamp as a field on the data structure where we store the price and block number. I've also added a test case to prevent regressions and show correctness
> 
> Since the exchange rate's timestamp is not actually used to signal an expiry in the protocol (it's only stored to make this query for the EVM), I'd maybe argue that this isn't high risk but more so a medium when compared with other tickets. 

**[berndartmueller (judge) decreased severity to Medium and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/2#issuecomment-2585269726):**
 > After more consideration, I consider this issue to be Medium severity. 
> 
> The chosen High severity is really borderline and has likely been determined on the assumption that the oracle prices are outdated/stale. However, this represents an [_external requirement_](https://docs.code4rena.com/awarding/judging-criteria/severity-categorization#estimating-risk), justifying Medium severity. This also aligns with issues in other audits that highlight the incorrect use of Chainlink's `latestAnswer()`, judged as Medium severity.

**Nibiru mitigated:**
> [PR-2117](https://github.com/NibiruChain/nibiru/pull/2117) - Added timestamps for exchange rates.

**Status:** Mitigation confirmed. 

***
