# Nibiru C4 M-07: Nonce can be manipulated by inserting a contract creation EthereumTx first in an SDK TX with multiple EthereumTX messages

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2024-11-m07-batched-evm-nonce-replay`

---

## [[M-07] Nonce can be manipulated by inserting a contract creation `EthereumTx` message first in an SDK TX with multiple `EthereumTX` messages](https://github.com/code-423n4/2024-11-nibiru-findings/issues/29)
*Submitted by [Sentryx](https://github.com/code-423n4/2024-11-nibiru-findings/issues/29)*

The Ante handler for `MsgEthereumTx` transactions is responsible for ensuring messages are coming with correct nonces. After doing so, it'll increment the account's sequences for each message that the account has signed and broadcasted.

The problem is that when the `EthereumTx()` message server method calls `ApplyEvmMsg()` it'll override the account nonce when the currently processed EVM transaction message is a contract creation and will set it to the nonce of the message. When a non-contract creation EVM transaction message is processed, however, the `ApplyEvmMsg()` method does **not** touch the account's nonce.

This opens up an exploit window where a malicious user can replay a TX multiple times and reuse their nonces. Users can manipulate their Sequence (nonce) by submitting a contract creation EVM transaction message and multiple call/transfer EVM transaction messages in a single SDK transaction.

The code relies on `evmObj.Call()` and later `stateDB.commitCtx()` to persist a correct nonce in state but the `Call()` method on `evmObj` does **not** handle account nonces, it just executes the transaction. As we can see the method in `geth` that's normally used to transition the state increments the sender's nonce by 1 in either case:

<https://github.com/NibiruChain/go-ethereum/blob/nibiru/geth/core/state_transition.go#L331-L337>

```go
	if contractCreation {
		ret, _, st.gas, vmerr = st.evm.Create(sender, st.data, st.gas, st.value)
	} else {
		// Increment the nonce for the next transaction
		st.state.SetNonce(msg.From(), st.state.GetNonce(sender.Address())+1)
		ret, st.gas, vmerr = st.evm.Call(sender, st.to(), st.data, st.gas, st.value)
	}
```

<https://github.com/NibiruChain/go-ethereum/blob/nibiru/geth/core/vm/evm.go#L498-L501>

```go
func (evm *EVM) Create(caller ContractRef, code []byte, gas uint64, value *big.Int) (ret []byte, contractAddr common.Address, leftOverGas uint64, err error) {
	contractAddr = crypto.CreateAddress(caller.Address(), evm.StateDB.GetNonce(caller.Address()))
	return evm.create(caller, &codeAndHash{code: code}, gas, value, contractAddr, CREATE)
}
```

<https://github.com/NibiruChain/go-ethereum/blob/7fb652f186b09b81cce9977408e1aff744f4e3ef/core/vm/evm.go#L405-L418>

```go
func (evm *EVM) create(caller ContractRef, codeAndHash *codeAndHash, gas uint64, value *big.Int, address common.Address, typ OpCode) ([]byte, common.Address, uint64, error) {
	// Depth check execution. Fail if we're trying to execute above the
	// limit.
	if evm.depth > int(params.CallCreateDepth) {
		return nil, common.Address{}, gas, ErrDepth
	}
	if !evm.Context.CanTransfer(evm.StateDB, caller.Address(), value) {
		return nil, common.Address{}, gas, ErrInsufficientBalance
	}
	nonce := evm.StateDB.GetNonce(caller.Address())
	if nonce+1 < nonce {
		return nil, common.Address{}, gas, ErrNonceUintOverflow
	}
	evm.StateDB.SetNonce(caller.Address(), nonce+1)
```

But `ApplyEvmMsg()` calls `evmObj.Call()` (`st.evm.Call()` in the above code snippet) directly and does not increment sender's nonce:

```go
	if contractCreation {
		// take over the nonce management from evm:
		// - reset sender's nonce to msg.Nonce() before calling evm.
		// - increase sender's nonce by one no matter the result.
		stateDB.SetNonce(sender.Address(), msg.Nonce())
		ret, _, leftoverGas, vmErr = evmObj.Create(
			sender,
			msg.Data(),
			leftoverGas,
			msgWei,
		)
		stateDB.SetNonce(sender.Address(), msg.Nonce()+1)
	} else {
		ret, leftoverGas, vmErr = evmObj.Call(
			sender,
			*msg.To(),
			msg.Data(),
			leftoverGas,
			msgWei,
		)
	}
```

### Proof of Concept

1. User constructs an **SDK** transaction with 4 `MsgEthereumTx` messages in it.
2. The first message is an **EVM** transaction that creates a new contract and has a nonce 1.
3. The next three messages are also **EVM** transactions that transfer ether (unibi as its the native unit of account in Nibiru's EVM) or just call some contracts.
4. The three messages have nonces of 2, 3 and 4.
5. The user broadcasts the **SDK** transaction. It passes validation through the Ante handler and is included in the mempool.
6. The TX is picked up to be processed by the `DeliverTx()` method and the Ante handler is called again.
7. The Ante handler increments the `MsgEthereumTx` message sender's sequence (nonce) for each **EVM** transaction message.
8. User's sequence (nonce) in their SDK `x/auth` account is currently 5 (the next consecutive ready-for-use nonce).
9. `ApplyEvmMsg()` is called to process the first **EVM** transaction message and since it's a contract creation transaction it sets the sender's sequence (nonce) to `msg.Nonce() + 1`. After running the transaction through the geth interpreter, the account `stateObject` properties (like nonce, code hash and account state) are persisted to the `x/evm` module keeper's storage by calling `stateDB.Commit()`. The user account's `Sequence` is now reset to `msg.Nonce() + 1` (equal to 2).
10. The remaining three messages with nonces (2, 3, and 4) are then executed but the user's sequence (nonce) is still at `2`.
11. User can now replay their last three messages.

| SDK TX Message # | Contract creation | Message nonce | Account sequence set by ante handler | Account sequence after execution |
| ---------------- | ------- | ------- | ---------- | --------- |
| 1 | true | 1 | 1 | 1 (set by `ApplyEvmMsg()`) |
| 2 | false | 2 | 2 | 1 (not updated as `contractCreation == false`) |
| 3 | false | 3 | 3 | 1 |
| 4 | false | 4 | 4 | 1 |

### Recommended mitigation steps

Set the sender's nonce to `msg.Nonce() + 1` when `contractCreation` is `false`.

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/29#issuecomment-2543335735):**
 > Initially, I assumed that only a single EVM message is supported, due to `MsgEthereumTx.GetMsgs()` returning only a single message.
> 
> https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/x/evm/msg.go#L190-L193
> 
> ```go
> 190: // GetMsgs returns a single MsgEthereumTx as sdk.Msg.
> 191: func (msg *MsgEthereumTx) GetMsgs() []sdk.Msg {
> 192: 	return []sdk.Msg{msg}
> 193: }
> ```
> 
> However, that's not the correct `GetMsgs()`. In fact, multiple EVM messages within a single Cosmos tx **are** supported. As a result, the demonstrated issue is valid, allowing replaying a user's EVM messages in this specific scenario. That's a great catch!

**[k-yang (Nibiru) confirmed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/29#issuecomment-2553713417):**
 > Agree it's a valid issue.

**[onikonychev (Nibiru) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/29#issuecomment-2559443233):**
> @berndartmueller - and this is true so far. That's why we have a separate Ante handler which does not allow `MsgEthereumTx` within Cosmos TXs: https://github.com/NibiruChain/nibiru/blob/main/app/ante/reject_ethereum_tx_msgs.go
> 
> I don't think there is a backdoor for sending a bulk of `MsgEthereumTx`.

**[Unique-Divine (Nibiru) disputed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/29#issuecomment-2561362844):**
 > ### Rebuttal to the Proposed Vulnerability
> 
> I'd argue the side of `sponsor-disputed` here, similar to @onikonychev. When every transaction goes through execution via the `DeliverTx` ABCI (application blockchain interface) method. The implementation details of this function can be seen in `BaseApp.runTx` from the Cosmos-SDK baseapp/bapp.go code that, as it implements much of the non-consensus side of the ABCI.
> 
> In `BaseApp.runTx`, it first gets each message and calls `ValidateBasic` on them, then it enters the `BaseApp.anteHandler` before beginning any other logic with the tx msgs.
> 
> *Note: to view the provided image, please see the original comment [here](https://github.com/code-423n4/2024-11-nibiru-findings/issues/29#issuecomment-2561362844).*
> 
> The Nibiru ante handler, instantiated with `NewAnteHandler` in Nibiru/app/ante.go splits a tx down different paths of potential ante handlers. 
> 
> You can see below that, if a tx (`sdk.Tx`) comes in and has the properties indicating it's an `sdk.Tx` that is also a `MsgEthereumTx`, then it passes through an EVM ante handler (`evmante.NewAnteHandlerEVM`). 
> 
> If however, the `sdk.Tx` is anything else, it goes through a non-EVM ante handler (`NewAnteHandlerNonEVM`), which you'll see has the very first `sdk.ChainAnteDecorator` hook as a blocker that disallows the execution of the `sdk.Tx` if any of the contained messages are `evm.MsgEthereumTx` instances. 
>  
> > *Note:* Thus, it is not possible to insert a contract creation EthereumTx message in a non-EVM `sdk.Tx` with multiple EthereumTx messages because that type of tx would be rejected in the ante handler, even if there was only one `MsgEthereumTx` contained in the `sdk.Tx`
> 
> ```go
> // NewAnteHandler returns and AnteHandler that checks and increments sequence
> // numbers, checks signatures and account numbers, and deducts fees from the
> // first signer.
> func NewAnteHandler(
> 	keepers AppKeepers,
> 	options ante.AnteHandlerOptions,
> ) sdk.AnteHandler {
> 	return func(
> 		ctx sdk.Context, tx sdk.Tx, sim bool,
> 	) (newCtx sdk.Context, err error) {
> 		if err := options.ValidateAndClean(); err != nil {
> 			return ctx, err
> 		}
> 
> 		var anteHandler sdk.AnteHandler
> 		txWithExtensions, ok := tx.(authante.HasExtensionOptionsTx)
> 		if ok {
> 			opts := txWithExtensions.GetExtensionOptions()
> 			if len(opts) > 0 {
> 				switch typeURL := opts[0].GetTypeUrl(); typeURL {
> 				case "/eth.evm.v1.ExtensionOptionsEthereumTx":
> 					// handle as *evmtypes.MsgEthereumTx
> 					anteHandler = evmante.NewAnteHandlerEVM(options)
> 				default:
> 					return ctx, fmt.Errorf(
> 						"rejecting tx with unsupported extension option: %s", typeURL)
> 				}
> 
> 				return anteHandler(ctx, tx, sim)
> 			}
> 		}
> 
> 		switch tx.(type) {
> 		case sdk.Tx:
> 			anteHandler = NewAnteHandlerNonEVM(options)
> 		default:
> 			return ctx, fmt.Errorf("invalid tx type (%T) in AnteHandler", tx)
> 		}
> 		return anteHandler(ctx, tx, sim)
> 	}
> }
> ```
> 
> ### Why is this confusing at first glance?
> 
> The term transaction is overused in Web3 and means different things in the EVM context than in the ABCI/Cosmos-SDK context. An Ethereum tx can contain several Ethereum txs inside it. In other words, what's called a tx msg or simply a "message" in the ABCI is what's analogous to the idea of an Ethereum Tx, not the `sdk.Tx`. 
> 
> `MsgEthereumTx` is meant to represent a true "Ethereum tx" like on the Eth L1. That means, a `MsgEthereumTx` may induce one or more inner Ethereum txs; however, they'll only be still only occur within that single `MsgEthereumTx`. 

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/29#issuecomment-2561382233):**
 > @Unique-Divine - this issue is about multiple EVM messages within a single Cosmos TX. It’s not mixing EVM and regular msg’s; therefore, the EVM ante handler is used. It can, however, be argued on the severity.

**[flacko (warden) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/29#issuecomment-2561410501):**
 > Here's the POC in question: https://gist.github.com/flackoon/17123ba138c3e07816a76e191a0bf34d.
>
> The matter really is about putting multiple EVM transactions in a single SDK transaction. In this POC the two contract call transactions are replayable as the nonce got incremented only once because of how `ApplyEvmMsg` handles the nonce.

**[berndartmueller (judge) decreased severity to Medium and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/29#issuecomment-2579529958):**
 > According to C4's [severity categorization](https://docs.code4rena.com/awarding/judging-criteria/severity-categorization#estimating-risk), given that there's no direct impact on assets or liveness, I'm downgrading to Medium severity.

**Nibiru mitigated:**
> [PR-2130](https://github.com/NibiruChain/nibiru/pull/2130) - Proper nonce management in `statedb`.

**Status:** Mitigation confirmed. 

***
