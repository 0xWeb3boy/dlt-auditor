---
case_id: case_20240129_78e3cbb884
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
bug_class: consensus-safety
source_quality: medium
date: 2024-01-29
source_refs:
  - git:78e3cbb884d318e3362fa38f579d55fec8fb4387
  - "op-program/client/l2/engineapi/block_processor.go:81"
  - "op-node/rollup/derive/ecotone_upgrade_transactions_test.go:111"
  - "op-bindings/predeploys/eip4788.go:11"
  - "op-node/rollup/derive/ecotone_upgrade_transactions.go:35"
impact_type:
  - consensus-divergence-risk
  - state-transition-risk
confidence: medium
tags:
  - blockchain-core
  - consensus-sensitive
  - protocol-upgrade
  - eip-4788
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is clearly fixing Ecotone/EIP-4788 protocol-correctness logic, but the provided evidence does not firmly establish a security vulnerability beyond possible post-fork state mismatch risk.

## Observed Patch Facts

1. In `op-program/client/l2/engineapi/block_processor.go`, the patch replaces `return &BlockProcessor{` with `if h.ParentBeaconRoot != nil {`.

2. In `op-node/rollup/derive/ecotone_upgrade_transactions_test.go`, the patch replaces `require.Equal(t, eip4788CreationData, common.Hex2Bytes("0x60618060095f395ff33373fffff...` with `require.NotEmpty(t, beaconRoots.Data())`.

3. In `op-bindings/predeploys/eip4788.go`, the patch replaces `EIP4788ContractAddr = common.HexToAddress("0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02")` with `EIP4788ContractAddr = common.HexToAddress("0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02")`.

4. In `op-node/rollup/derive/ecotone_upgrade_transactions.go`, the patch replaces `eip4788CreationData = common.Hex2Bytes("0x60618060095f395ff33373fffffffffffffffffffff...` with `eip4788CreationData = common.FromHex("0x60618060095f395ff33373fffffffffffffffffffffff...`.

## Project Context

The changed code sits primarily in `op-program/client/l2/engineapi`, `op-program/client/l2`, `op-node/rollup/derive`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `op-node/rollup/derive/channel_out_test.go`, `op-program/client/l2/engineapi/l2_engine_api.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-node/rollup/derive/channel_out_test.go`, `op-program/client/l2/oracle_test.go`. The strongest project-level identifiers around this patch are `common`, `require`, `eip4788CreationData`, and `header`. Nearby tests or test-like files include `op-node/rollup/derive/fuzz_parsers_test.go`, `op-program/client/l2/engineapi/test/l2_engine_api_tests.go`.

## Before/After Behavior

Before the patch, the Ecotone upgrade code built the beacon-roots deployment payload with common.Hex2Bytes("0x..."), tests did not independently assert the payload was non-empty, and NewBlockProcessorFromHeader returned without any ParentBeaconRoot-specific processing. After the patch, the byte constants use common.FromHex("0x..."), an EIP4788ContractCodeHash constant is added, tests assert the payload is non-empty, and NewBlockProcessorFromHeader explicitly calls core.ProcessBeaconBlockRoot when ParentBeaconRoot is present.

# Root Cause

Ecotone-specific EIP-4788 handling was incomplete or inconsistently represented: one path used a different hex-decoding helper for deterministic bytecode, and one block-processor constructor omitted the explicit ParentBeaconRoot processing step.

## Walkthrough

1. op-node/rollup/derive/ecotone_upgrade_transactions.go changes eip4788CreationData from common.Hex2Bytes("0x...") to common.FromHex("0x...").

2. op-bindings/predeploys/eip4788.go makes the same helper change for the deployed code constant and adds EIP4788ContractCodeHash.

3. op-node/rollup/derive/ecotone_upgrade_transactions_test.go adds non-empty assertions and compares against the FromHex form, showing the patch is concerned with the exact deployment bytes.

4. op-program/client/l2/engineapi/block_processor.go now checks whether ParentBeaconRoot is present and calls core.ProcessBeaconBlockRoot before continuing block processing.

5. Taken together, the patch repairs Ecotone beacon-root deployment and header-processing correctness, but the evidence does not prove exploitation or real network divergence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-node/rollup/derive/ecotone_upgrade_transactions.go | 35 | Constructs the Ecotone upgrade deposit transaction payload that deploys the EIP-4788 beacon-block-roots contract. |
| op-bindings/predeploys/eip4788.go | 5 | Defines the canonical deployed EIP-4788 bytecode and expected code hash used as the correctness baseline for the deployment result. |
| op-program/client/l2/engineapi/block_processor.go | 81 | Builds block-execution state and now applies the `ParentBeaconRoot` processing step required for correct post-fork state transitions. |

## Code Snippets

## Snippet 1

Context: `op-program/client/l2/engineapi/block_processor.go:81` (changes a sensitive control or state-update path)

Before
```go
header.GasUsed = 0
	gasPool := new(core.GasPool).AddGas(header.GasLimit)
	return &BlockProcessor{
		header:       header,
```
After
```go
header.GasUsed = 0
	gasPool := new(core.GasPool).AddGas(header.GasLimit)
	if h.ParentBeaconRoot != nil {
		// Unfortunately this is not part of any Geth environment setup,
		// we just have to apply it, like how the Geth block-builder worker does.
		context := core.NewEVMBlockContext(header, provider, nil, provider.Config(), statedb)
		vmenv := vm.NewEVM(context, vm.TxContext{}, statedb, provider.Config(), vm.Config{})
		core.ProcessBeaconBlockRoot(*header.ParentBeaconRoot, vmenv, statedb)
```

## Snippet 2

Context: `op-node/rollup/derive/ecotone_upgrade_transactions_test.go:111` (changes a sensitive control or state-update path)

Before
```go
require.Equal(t, uint64(250_000), beaconRoots.Gas())
	require.Equal(t, eip4788CreationData, beaconRoots.Data())
}

func TestEip4788Params(t *testing.T) {
	require.Equal(t, EIP4788From, common.HexToAddress("0x0B799C86a49DEeb90402691F1041aa3AF2d3C875"))
	require.Equal(t, eip4788CreationData, common.Hex2Bytes("0x60618060095f395ff33373fffffffffffffffffffffffffffffffffffffffe14604d57602036146024575f5ffd5b5f35801560495762001fff810690815414603c575f5ffd5b62001fff01545f5260205ff35b5f5ffd5b62001fff42064281555f359062001fff015500"))
}
```
After
```go
require.Equal(t, uint64(250_000), beaconRoots.Gas())
	require.Equal(t, eip4788CreationData, beaconRoots.Data())
	require.NotEmpty(t, beaconRoots.Data())
}

func TestEip4788Params(t *testing.T) {
	require.Equal(t, EIP4788From, common.HexToAddress("0x0B799C86a49DEeb90402691F1041aa3AF2d3C875"))
	require.Equal(t, eip4788CreationData, common.FromHex("0x60618060095f395ff33373fffffffffffffffffffffffffffffffffffffffe14604d57602036146024575f5ffd5b5f35801560495762001fff810690815414603c575f5ffd5b62001fff01545f5260205ff35b5f5ffd5b62001fff42064281555f359062001fff015500"))
```

## Snippet 3

Context: `op-bindings/predeploys/eip4788.go:11` (changes a sensitive control or state-update path)

Before
```go
// And https://eips.ethereum.org/EIPS/eip-4788
var (
	EIP4788ContractAddr = common.HexToAddress("0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02")
	EIP4788ContractCode = common.Hex2Bytes("0x3373fffffffffffffffffffffffffffffffffffffffe14604d57602036146024575f5ffd5b5f35801560495762001fff810690815414603c575f5ffd5b62001fff01545f5260205ff35b5f5ffd5b62001fff42064281555f359062001fff015500")
)
```
After
```go
// And https://eips.ethereum.org/EIPS/eip-4788
var (
	EIP4788ContractAddr     = common.HexToAddress("0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02")
	EIP4788ContractCode     = common.FromHex("0x3373fffffffffffffffffffffffffffffffffffffffe14604d57602036146024575f5ffd5b5f35801560495762001fff810690815414603c575f5ffd5b62001fff01545f5260205ff35b5f5ffd5b62001fff42064281555f359062001fff015500")
	EIP4788ContractCodeHash = common.HexToHash("0xf57acd40259872606d76197ef052f3d35588dadf919ee1f0e3cb9b62d3f4b02c")
)
```

## Snippet 4

Context: `op-node/rollup/derive/ecotone_upgrade_transactions.go:35` (changes a sensitive control or state-update path)

Before
```go
EIP4788From         = common.HexToAddress("0x0B799C86a49DEeb90402691F1041aa3AF2d3C875")
	eip4788CreationData = common.Hex2Bytes("0x60618060095f395ff33373fffffffffffffffffffffffffffffffffffffffe14604d57602036146024575f5ffd5b5f35801560495762001fff810690815414603c575f5ffd5b62001fff01545f5260205ff35b5f5ffd5b62001fff42064281555f359062001fff015500")
	UpgradeToFuncBytes4 = crypto.Keccak256([]byte(UpgradeToFuncSignature))[:4]
```
After
```go
EIP4788From         = common.HexToAddress("0x0B799C86a49DEeb90402691F1041aa3AF2d3C875")
	eip4788CreationData = common.FromHex("0x60618060095f395ff33373fffffffffffffffffffffffffffffffffffffffe14604d57602036146024575f5ffd5b5f35801560495762001fff810690815414603c575f5ffd5b62001fff01545f5260205ff35b5f5ffd5b62001fff42064281555f359062001fff015500")
	UpgradeToFuncBytes4 = crypto.Keccak256([]byte(UpgradeToFuncSignature))[:4]
```

# Fix Pattern

Add the missing protocol-specific execution hook and tighten deterministic artifact encoding/tests around the upgrade payload.

## How It Was Fixed

The fix switches the EIP-4788 byte constants to common.FromHex, adds an explicit code-hash constant for the deployed contract, strengthens tests to reject empty deployment data, and injects ProcessBeaconBlockRoot into block-processor initialization when ParentBeaconRoot is set.

# Why It Matters

1. Wrong upgrade bytecode can change what contract gets deployed at the fork.

2. Skipping ParentBeaconRoot processing can change post-fork derived state.

3. These changes affect protocol correctness, even though direct security impact is not proven here.

# Evidence Notes

Direct evidence shows a missing ProcessBeaconBlockRoot call was added in block_processor.go and the EIP-4788 byte constants were changed from Hex2Bytes to FromHex with stronger tests. It is reasonable to infer the old code could mishandle Ecotone beacon-root deployment or state application. However, the provided material does not show an actual exploit, authorization failure, fund loss, or confirmed production consensus split, and it does not independently prove the old Hex2Bytes form produced an incorrect value in practice. Protocol security invariant: Post-Ecotone handling should use the intended EIP-4788 deployment bytes and should apply the beacon-root state update whenever a header carries ParentBeaconRoot, so derived execution state matches the protocol rules. Verification notes: The patch does not prove an attacker could arbitrarily set beacon roots or bypass an authorization check. The evidence does not show fund theft, key compromise, or a classic memory-corruption issue. The patch alone does not prove that production networks actually diverged or that the wrong bytecode was live on mainnet. Exploitability is not demonstrated beyond consensus/upgrade-correctness failure if nodes execute the old logic. Tests were updated alongside the implementation changes. The evidence supports a protocol-correctness fix more strongly than a confirmed vulnerability. No proof of mainnet impact or exploitability is included in the provided record. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `consensus-divergence-risk, state-transition-risk`
Final confidence: `medium`
Final tags: `blockchain-core, consensus-sensitive, protocol-upgrade, eip-4788`

The patch is not a proven exploitable security bug, but it does tighten a consensus-sensitive execution path in blockchain-core code. The strongest evidence is the newly added `ProcessBeaconBlockRoot` call during block processing when `ParentBeaconRoot` is present, plus correction and validation of deterministic EIP-4788 deployment bytes. That supports retaining this as security-hardening because it reduces protocol state-integrity and consensus-divergence risk, while stopping short of claiming a confirmed vulnerability or real-world exploit.

## Security Evidence

1. Adds `core.ProcessBeaconBlockRoot(...)` when `ParentBeaconRoot` is present, changing actual state-transition behavior in block processing.
2. Corrects EIP-4788 byte handling from `Hex2Bytes("0x...")` to `FromHex("0x...")`, consistent with tests that now assert non-empty deployment data.
3. Adds a canonical EIP-4788 contract code hash, indicating stricter verification of deployed contract code.
4. Touches upgrade and execution-path code, not only tests or refactoring, in a consensus-critical subsystem.

## Missing Evidence

1. No advisory, CVE, or commit text explicitly states a security vulnerability.
2. No proof of attacker-triggerable exploit, fund loss, or authorization bypass.
3. No direct evidence that the old behavior caused a live consensus split or production incident.
4. No demonstration that the previous byte-decoding bug was externally exploitable beyond protocol-correctness failure.

## Claim Boundaries

1. Supported: this patch hardens protocol/consensus correctness in a security-sensitive path.
2. Supported: prior behavior risked incorrect state application or incorrect upgrade artifact handling.
3. Not supported: a confirmed exploitable security vulnerability.
4. Not supported: proven consensus failure, theft, privilege escalation, or real-world compromise.
