# Nibiru C4 M-06: RPC DoS via TraceTx

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2024-11-m06-tracetx-unbounded-predecessors`

---

## [[M-06] RPC DOS via `TraceTx`](https://github.com/code-423n4/2024-11-nibiru-findings/issues/35)
*Submitted by [gxh191](https://github.com/code-423n4/2024-11-nibiru-findings/issues/35)*

The `TraceTx` method in `x/evm/keeper/grpc_query.go` implements a gRPC query interface that allows simulation and tracing of specific transactions based on provided configurations. This method enables users to perform detailed execution simulations for transactions in a block.

However, a DOS issue arises during the simulation of predecessor transactions.

### Proof of Concept

Within the `TraceTx` function, predecessor transactions are simulated first, followed by transaction tracing:

<https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/grpc_query.go#L547>

```go
result, _, err := k.TraceEthTxMsg(ctx, cfg, txConfig, msg, req.TraceConfig, false, tracerConfig)
if err != nil {
    // error will be returned with detailed status from traceTx
    return nil, err
}
```

During the simulation of predecessor transactions, an attacker can exploit the process by providing an excessively large number of transactions in the `req.Predecessors` parameter. This forces the chain to repeatedly compute transaction results, maliciously consuming resources and leading to a denial of service.

<https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/grpc_query.go#L511>

```go
for i, tx := range req.Predecessors {
    ethTx := tx.AsTransaction()
    msg, err := ethTx.AsMessage(signer, cfg.BaseFeeWei)
    if err != nil {
        continue
    }
    txConfig.TxHash = ethTx.Hash()
    txConfig.TxIndex = uint(i)
    ctx = ctx.WithGasMeter(eth.NewInfiniteGasMeterWithLimit(msg.Gas())).
        WithKVGasConfig(storetypes.GasConfig{}).
        WithTransientKVGasConfig(storetypes.GasConfig{})
    rsp, _, err := k.ApplyEvmMsg(ctx, msg, evm.NewNoOpTracer(), true, cfg, txConfig, false)
    if err != nil {
        continue
    }
    txConfig.LogIndex += uint(len(rsp.Logs))
}
```

An attacker only needs to send an RPC query with an excessively large `--predecessors` parameter to trigger the DOS:

```
nibid query evm trace-tx \
  --block-number 100 \
  --block-time "2024-11-18T00:00:00Z" \
  --block-hash "0x123abc..." \
  --proposer-address "nibiru1xyz..." \
  --predecessors '[{"hash":"0x456def...","nonce":1,"from":"0xabc123...","to":"0xdef456..."}]' \
  --msg '{"hash":"0x789ghi...","nonce":2,"from":"0xabc123...","to":"0xdef456...","data":"0x..."}' \
  --trace-config '{"disableStorage":false,"disableMemory":false}'
```

### Recommended mitigations

- **Limit the number of predecessor transactions**: Set an upper bound on the number of transactions allowed in `req.Predecessors` to prevent resource abuse.
- **Enforce a total gas consumption limit**: Add a global gas consumption restriction for the simulation process to avoid infinite computation scenarios.
- Add timeout limitation.

Similar to the timeout mechanism in `TraceEthTxMsg`, a timeout restriction can be implemented to mitigate potential abuse:

```go
func (k *Keeper) TraceEthTxMsg(
    ctx sdk.Context,
    cfg *statedb.EVMConfig,
    txConfig statedb.TxConfig,
    msg gethcore.Message,
    traceConfig *evm.TraceConfig,
    commitMessage bool,
    tracerJSONConfig json.RawMessage,
) (*any, uint, error) {
    // Assemble the structured logger or the JavaScript tracer
    var (
        tracer    tracers.Tracer
        overrides *gethparams.ChainConfig
        err       error
        timeout   = DefaultGethTraceTimeout
    )
    if traceConfig == nil {
        traceConfig = &evm.TraceConfig{}
    }

    ...
}

// Re-export of the default tracer timeout from go-ethereum.
// See "geth/eth/tracers/api.go".
const DefaultGethTraceTimeout = 5 * time.Second
```

By adding a similar timeout limitation, the execution of `TraceTx` can be bound within a reasonable time frame. This reduces the risk of excessive resource consumption caused by intentionally large input parameters or malicious queries.

**[berndartmueller (judge) decreased severity to Medium](https://github.com/code-423n4/2024-11-nibiru-findings/issues/35#issuecomment-2555114895)**

**[k-yang (Nibiru) acknowledged and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/35#issuecomment-2571384772):**
 > Agree that it's a DoS vector, but it's not a state-mutating endpoint and public facing JSON RPC endpoints are really up to the node runners to serve and protect.
> 
> We may get around to implementing the suggestions at some point in the future, but it seems very low priority at the moment.

***
