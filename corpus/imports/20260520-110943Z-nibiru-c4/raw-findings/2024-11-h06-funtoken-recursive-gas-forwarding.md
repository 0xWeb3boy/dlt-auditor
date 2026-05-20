# Nibiru C4 H-06: Hardcoded gas used in ERC20 queries allows block production halt from infinite recursion

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `High`
- Corpus ID: `nibiru-c4-2024-11-h06-funtoken-recursive-gas-forwarding`

---

## [[H-06] Hardcoded gas used in ERC20 queries allows for block production halt from infinite recursion](https://github.com/code-423n4/2024-11-nibiru-findings/issues/4)
*Submitted by [3docSec](https://github.com/code-423n4/2024-11-nibiru-findings/issues/4), also found by [0x007](https://github.com/code-423n4/2024-11-nibiru-findings/issues/22)*

<https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/x/evm/precompile/funtoken.go#L149>

<https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/x/evm/precompile/funtoken.go#L285>

### Vulnerability details

The `funtoken` precompile allows an EVM caller to access information about tokens that coexist in the Cosmos ("coin") and EVM ("ERC20") spaces.

Some operations performed by this precompile consist of EVM calls; for example, if we look at the `balance` method:

```go
File: funtoken.go
265: func (p precompileFunToken) balance(
266: 	start OnRunStartResult,
267: 	contract *vm.Contract,
268: ) (bz []byte, err error) {
---
285: 	erc20Bal, err := p.evmKeeper.ERC20().BalanceOf(funtoken.Erc20Addr.Address, addrEth, ctx)
286: 	if err != nil {
287: 		return
288: 	}
```

We see that for fetching the EVM info, it calls the `evmKeeper.ERC20().BalanceOf` function:

```go
File: erc20.go
125: func (e erc20Calls) BalanceOf(
126: 	contract, account gethcommon.Address,
127: 	ctx sdk.Context,
128: ) (out *big.Int, err error) {
129: 	return e.LoadERC20BigInt(ctx, e.ABI, contract, "balanceOf", account)
130: }
```

Which in turn calls `LoadERC20BigInt`:

```go
File: erc20.go
222: func (k Keeper) LoadERC20BigInt(
223: 	ctx sdk.Context,
224: 	abi *gethabi.ABI,
225: 	contract gethcommon.Address,
226: 	methodName string,
227: 	args ...any,
228: ) (out *big.Int, err error) {
229: 	res, err := k.CallContract(
230: 		ctx,
231: 		abi,
232: 		evm.EVM_MODULE_ADDRESS, // @audit from
233: 		&contract,
234: 		false, // @audit commit = false
235: 		Erc20GasLimitQuery, // @audit 100_000
236: 		methodName,
237: 		args...,
238: 	)
239: 	if err != nil {
240: 		return nil, err
241: 	}
```

If we look closely to how this callback to the EVM is done, we see that the gas allowed for this call is hardcoded to `100_000` and is charged only after the call returned.

This is problematic because `100_000` is allocated regardless of the gas limit used to call the `funtoken` precompile, and this breaks the [core invariant of the 63/64 gas allocation](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-150.md) that ultimately secures EVM implementation from infinite recursions, which can halt block production and cause the validator to be slashed.

While the `balance` example was described in detail, the same applies to the `Transfer` call in `sendToBank`:

```go
File: funtoken.go
109: func (p precompileFunToken) sendToBank(
110: 	startResult OnRunStartResult,
111: 	caller gethcommon.Address,
112: 	readOnly bool,
113: ) (bz []byte, err error) {
---
149: 	gotAmount, transferResp, err := p.evmKeeper.ERC20().Transfer(erc20, caller, transferTo, amount, ctx)
150: 	if err != nil {
151: 		return nil, fmt.Errorf("error in ERC20.transfer from caller to EVM account: %w", err)
152: 	}
```

The `Burn` call in `sendToBank` is instead secure because it only applies to ERC20 tokens deployed from Coins whose EVM contract is safe.

### Proof of Concept

**For the `balance/balanceOf` attack path,** (and a more comprehensive, but slower, end-to-end test), this [GitHub Gist](https://gist.github.com/3docSec/7e8f04b601d08fb8af0319179da10e33) includes a coded PoC in the form of an e2e test that:

- Creates an attack ERC-20 token with a function that calls itself through the `funtoken` precompile.
- Registers this token as `funtoken` (the call takes a fee but is otherwise permissionless).
- Calls the infinite recursing function.

This test can be run while monitoring the memory consumption of the `localnet` `nibid` process:

- Before the test, the `nibd` process consumes steadily `~100Mb` of memory.
- After the `go()` call is triggered:
    - Memory consumption increases at `~10Mb/sec` until `nibd` gets eventually killed.
    - Even during memory ramp up, the test network stops producing blocks due to consensus timeout.


**For the `sendToBank/transfer` attack path**, the infinite recursion can be tested by changing the `transfer` function in the `TestERC20MaliciousTransfer` test contract as follows:

```solidity
import "@openzeppelin/contracts/utils/Strings.sol";

    // ...

    function transfer(address to, uint256 amount) public override returns (bool) {
        (bool res, bytes memory data) = address(0x800).call(
            abi.encodeWithSignature(
                "sendToBank(address,uint256,string)",
                address(this),
                Strings.toHexString(uint160(to))
            )
        );
        require(res, string(data));
        return true;
    }
```

Then, running the `TestFunTokenFromERC20MaliciousTransfer` test in `x/evm/keeper/funtoken_from_erc20_test.go` will hang in an infinite recursion that will quickly eat up all memory available.

### Recommended Mitigation Steps

Consider refactoring the `evmKeeper.ERC20().BalanceOf` and `evmKeeper.ERC20().Transfer` calls to accept as argument, and use at most, 63/64 of the EVM gas available.

**[Unique-Divine (Nibiru) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/4#issuecomment-2500112601):**
 > Please label this as `sponsor confirmed`. I've not yet run the steps to reproduce the error case, but it seems legit from reading the description.

**[k-yang (Nibiru) confirmed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/4#issuecomment-2553738806):**
 > Agreed it's a valid issue.

**[onikonychev (Nibiru) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/4#issuecomment-2561368110):**
 > This is a great catch, indeed! I was able to crash my localnet with either recursive `balanceOf()` or `transfer()`.

**Nibiru mitigated:**
> [PR-2129](https://github.com/NibiruChain/nibiru/pull/2129) - Resolved an infinite recursion issue in ERC20 FunToken contracts.

**Status:** Mitigation confirmed. 

***

# Medium Risk Findings (10)
