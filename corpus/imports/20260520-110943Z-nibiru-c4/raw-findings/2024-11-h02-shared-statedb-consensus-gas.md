# Nibiru C4 H-02: Non-deterministic gas consumption due to shared StateDB pointer in bank keeper affecting consensus

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `High`
- Corpus ID: `nibiru-c4-2024-11-h02-shared-statedb-consensus-gas`

---

## [[H-02] Non-deterministic gas consumption due to shared `StateDB` pointer in bank keeper affecting consensus](https://github.com/code-423n4/2024-11-nibiru-findings/issues/57)
*Submitted by [0x41](https://github.com/code-423n4/2024-11-nibiru-findings/issues/57)*

An issue exists in Nibiru's implementation of the bank keeper and its interaction with the EVM's StateDB. The `NibiruBankKeeper` maintains a pointer field to `StateDB` that gets updated during read-only EVM operations (like `eth_estimateGas`), which then affects the gas computation of subsequent bank transactions.

The issue arises because the `StateDB` pointer in `NibiruBankKeeper` is modified during read-only operations, and the presence or absence of this pointer affects program flow in bank operations through nil checks:

```go
func (bk *NibiruBankKeeper) SyncStateDBWithAccount(ctx sdk.Context, acc sdk.AccAddress) {
    // If there's no StateDB set, it means we're not in an EthereumTx.
    if bk.StateDB == nil {
        return
    }
    // ... state updates
}
```

This can lead to consensus failures as different nodes may compute different gas amounts for the same transaction (depending on if they previously executed a read only query via RPC), which should never happen.

### Proof of Concept

The vulnerability can be demonstrated through the following sequence:

1. Initial state: Execute a bank send transaction and record gas used.

```go
// Initial bank send 
sendMsg := banktypes.NewMsgSend(sender, receiver, coins)
gasUsed1 := executeTx(sendMsg) // Records initial gas usage
```

2. Trigger a read-only operation that modifies the StateDB pointer.

```go
// This can modify NibiruBankKeeper.StateDB depending on the tx content
client.EstimateGas(ethTx) 
```

3. Execute the same bank send transaction again.

```go
gasUsed2 := executeTx(sendMsg) // Different gas usage than gasUsed1 because bk.StateDB is no longer nil
```

The key problematic code is in [`bank_extension.go`](https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/bank_extension.go):

```go
type NibiruBankKeeper struct {
    bankkeeper.BaseKeeper
    StateDB *statedb.StateDB  // This shared pointer causes the issue
}

func (evmKeeper *Keeper) NewStateDB(
    ctx sdk.Context, txConfig statedb.TxConfig,
) *statedb.StateDB {
    stateDB := statedb.New(ctx, evmKeeper, txConfig)
    evmKeeper.Bank.StateDB = stateDB // Modifies shared state
    return stateDB
}
```

### Recommended mitigation steps

There are several ways to fix this issue:

1. Clone the `StateDB` for read-only operations:

```go
func (k Keeper) EstimateGas(ctx sdk.Context, msg core.Message) (uint64, error) {
    originalStateDB := k.Bank.StateDB
    k.Bank.StateDB = originalStateDB.Copy()
    defer func() {
        k.Bank.StateDB = originalStateDB
    }()
    // ... estimation logic
}
```

2. Use context to pass `StateDB` instead of keeping it as a field:

```go
type NibiruBankKeeper struct {
    bankkeeper.BaseKeeper
}

func (bk *NibiruBankKeeper) SyncStateDBWithAccount(
    ctx sdk.Context, 
    stateDB *statedb.StateDB,
    acc sdk.AccAddress,
) {
    if stateDB == nil {
        return
    }
    // ... state updates
}
```

3. Implement a proper snapshot/restore mechanism:

```go
type BankKeeperState struct {
    stateDB *statedb.StateDB
}

func (bk *NibiruBankKeeper) Snapshot() *BankKeeperState {
    return &BankKeeperState{stateDB: bk.StateDB}
}

func (bk *NibiruBankKeeper) Restore(state *BankKeeperState) {
    bk.StateDB = state.stateDB
}
```

The solution must ensure:

- Deterministic gas computation across all nodes.
- Proper isolation between read-only and state-modifying operations.

**[Lambda (warden) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/57#issuecomment-2580993499):**
 > It is possible that I am missing something obvious and this is indeed invalid, but I still think that this is (was) a valid critical issue that could have caused consensus failure because of non-deterministic gas usage across nodes. While looking at the current Nibiri code, I even noticed that it was fixed in the meantime [here](https://github.com/NibiruChain/nibiru/pull/2110). However, this was in a later version than the frozen code, i.e., the frozen commit still had the issue.

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/57#issuecomment-2585205681):**
> @Lambda - After a more comprehensive second look, I agree that this is an issue. This finding was initially dismissed as invalid due to the lack of a comprehensive write-up and PoC. 
> 
> While this issue has been separately discovered by the sponsor, the code in scope of the audit still contained the flaw. Therefore, it's still a valid submission, with High severity justified, given that it can cause consensus failures.

**[k-yang (Nibiru) confirmed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/57#issuecomment-2619862473):**
 > Addressed by https://github.com/NibiruChain/nibiru/pull/2173.

**Nibiru mitigated:**
> [PR-2165](https://github.com/NibiruChain/nibiru/pull/2165) - Ensure only one copy of `StateDB` when executing Ethereum txts.

**Status:** Mitigation confirmed. 
***
