---
case_id: case_20180416_1166bb6a
project: thor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2018-04-16
source_refs:
  - git:1166bb6aecfbd05060d8cc5acde422fcf87846cb
  - "builtin/bridge.go:30"
  - "builtin/bridge.go:84"
  - "runtime/runtime.go:85"
  - "vm/evm/interpreter.go:117"
bug_class: native-contract-hook-dispatch-hardening
impact_type:
  - execution-context-integrity
confidence: medium
tags:
  - vm
  - evm
  - native-contract-hook
  - callcode
  - delegatecall
  - execution-context
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is security-relevant hardening of thor's VM builtin/native contract hook path, but the supplied evidence does not prove a concrete vulnerability. The strongest grounded change is that hook dispatch is moved into Interpreter.Run and gated so hooks run only when contract.CodeAddr equals contract.Address(), with an explicit comment that CALLCODE or DELEGATECALL should be ignored.

## Observed Patch Facts

1. In `builtin/bridge.go`, the patch replaces `vmCtx *vm.Context,` with `vm *evm.EVM,`.

2. In `builtin/bridge.go`, the patch replaces `// recoverable error, that can be passed to VM.` with `func (b *bridge) ParseArgs(val interface{}) {`.

3. In `runtime/runtime.go`, the patch replaces `to thor.Address,` with `evm *evm.EVM,`.

4. In `vm/evm/interpreter.go`, the patch replaces `// Don't bother with the execution if there's no code.` with `// handle contract hook`.

## Project Context

The changed code sits primarily in `vm/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `vm/evm/contract.go`, `vm/evm/contracts_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `vm/evm/logger.go`, `vm/evm/instructions.go`. The strongest project-level identifiers around this patch are `contract`, `state`, `input`, and `thor`.

## Before/After Behavior

Before the patch, runtime registered the contract hook using decomposed values such as destination, input, caller, gas callback, and log callback, and builtin bridge construction accepted those separate values. After the patch, runtime registers a hook that receives the active EVM and Contract objects, builtin bridge stores those objects, and Interpreter.Run dispatches the hook only when contract.CodeAddr is non-nil and equals contract.Address(). The bridge also now reads native input from b.Contract.Input and converts decode or Require failures into VM errors.

# Root Cause

The evidence supports a narrower root cause than a proven vulnerability: the native hook boundary previously depended on separately threaded call parameters rather than the active Contract object, and the provided hunks do not show the direct-code-execution guard that was added in the interpreter. It is not proven from the supplied evidence that this caused exploitable context confusion, state corruption, authorization bypass, node crash, or consensus failure.

## Walkthrough

1. Runtime execution registers a native contract hook for the VM.

2. Before the change, the hook API passed separate address, input, caller, gas, and log-related values into builtin handling.

3. After the change, the hook receives the active EVM and Contract objects.

4. Interpreter.Run now handles hook dispatch using the current Contract.

5. The interpreter checks that contract.CodeAddr is present and equals contract.Address() before invoking the hook.

6. The added comment says CALLCODE or DELEGATECALL should be ignored.

7. When dispatch is allowed, the interpreter assigns contract.Input from the current input and passes EVM, Contract, and read-only status to the hook.

8. The builtin bridge parses arguments from b.Contract.Input and returns VM errors for decode and Require failures.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| vm/evm/interpreter.go | 117 | Enforces native contract hook dispatch only for direct code execution and sets contract.Input before invoking the hook. |
| runtime/runtime.go | 85 | Registers the contract hook using EVM and Contract objects instead of decomposed call parameters. |
| builtin/bridge.go | 30 | Constructs the native-call bridge from state plus authoritative EVM/Contract context. |
| builtin/bridge.go | 84 | Converts native input decode failures and Require failures into VM errors handled by the bridge call path. |

## Code Snippets

## Snippet 1

Context: `builtin/bridge.go:30` (changes signature or replay validation logic)

Before
```go
method *nativeMethod,
	state *state.State,
	vmCtx *vm.Context,
	to thor.Address,
	input []byte,
	caller thor.Address,
	useGas func(uint64) bool,
	log func(*types.Log),
```
After
```go
method *nativeMethod,
	state *state.State,
	vm *evm.EVM,
	contract *evm.Contract,
) *bridge {
	return &bridge{
		method,
		state,
```

## Snippet 2

Context: `builtin/bridge.go:84` (changes persisted or aggregate state handling)

Before
```go
}

// recoverable error, that can be passed to VM.
// used at
// 1. parsing input data
// 2. use gas
// 3. require condition
type recoverable struct {
```
After
```go
}

func (b *bridge) ParseArgs(val interface{}) {
	if err := b.Method.ABI.DecodeInput(b.Contract.Input, val); err != nil {
		panic(&vmerror{errors.Wrap(err, "decode native input")})
	}
}
```

## Snippet 3

Context: `runtime/runtime.go:85` (changes persisted or aggregate state handling)

Before
```go
env := vm.New(ctx, rt.state, rt.vmConfig)
	env.SetContractHook(func(
		to thor.Address,
		input []byte,
		caller thor.Address,
		readonly bool,
		useGas func(gas uint64) bool,
		addLog func(vmlog *types.Log)) func() ([]byte, error) {
```
After
```go
env := vm.New(ctx, rt.state, rt.vmConfig)
	env.SetContractHook(func(
		evm *evm.EVM,
		contract *evm.Contract,
		readonly bool) func() ([]byte, error) {
		return builtin.HandleNativeCall(rt.state, evm, contract, readonly)
	})
	env.SetOnCreateContract(func(contractAddr thor.Address) {
```

## Snippet 4

Context: `vm/evm/interpreter.go:117` (changes a sensitive control or state-update path)

Before
```go
in.returnData = nil

	// Don't bother with the execution if there's no code.
	if len(contract.Code) == 0 {
```
After
```go
in.returnData = nil

	// handle contract hook
	if in.evm.contractHook != nil && contract.CodeAddr != nil {
		// ignore callcode or delegatecall
		if *contract.CodeAddr == contract.Address() {
			contract.Input = input
			if proc := in.evm.contractHook(
```

# Fix Pattern

Centralize native hook dispatch at the interpreter execution boundary and gate it on an explicit direct-code-execution check before calling builtin/native handling.

## How It Was Fixed

The hook interface was changed from decomposed call parameters to EVM and Contract objects. Runtime now passes those objects to builtin.HandleNativeCall. Interpreter.Run sets contract.Input and invokes the hook only when the executing code address matches the contract address. The builtin bridge now uses the Contract object for input parsing and VM error propagation.

# Why It Matters

1. Makes the native hook dispatch condition explicit in the interpreter.

2. Reduces reliance on separately threaded call context for builtin handling.

3. Preserves a clear distinction between direct contract execution and CALLCODE/DELEGATECALL-style execution.

4. Does not, on the provided evidence, prove a concrete security exploit or vulnerability impact.

# Evidence Notes

Grounded evidence comes from vm/evm/interpreter.go line 117, runtime/runtime.go line 85, and builtin/bridge.go lines 30 and 84. The commit subject includes security language, and the interpreter hunk explicitly comments that CALLCODE or DELEGATECALL should be ignored. Unsupported claims removed: malformed transaction crash, liveness failure, state theft, authorization bypass, consensus split, and confirmed remote exploitability. Protocol security invariant: Builtin/native contract hooks should only be invoked with the VM's active execution context, and hook dispatch should preserve the distinction between direct execution of a contract's own code and CALLCODE/DELEGATECALL-style execution. The patch adds an explicit CodeAddr == Address check before invoking the hook, but the provided evidence does not establish the concrete pre-patch vulnerability or exploit path. Verification notes: The provided patch does not prove a remotely exploitable attack path. The provided evidence does not show a concrete state theft, authorization bypass, or consensus split. The new prototype_energy and prototype_transferEnergy feature additions are not by themselves shown to be vulnerability fixes. The evidence does not prove malformed transaction input could crash a node. The precise pre-patch behavior of contract_ref.go, native_calls.go, and vm.go is not available beyond the summarized hunks. No concrete exploit path is shown in the supplied evidence. No tests demonstrating the vulnerable pre-patch behavior are included in the supplied evidence. The prototype_energy and prototype_transferEnergy additions are not shown to be vulnerability fixes. The precise old hook dispatch site is not shown, so the pre-patch impact remains inferred. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `native-contract-hook-dispatch-hardening`
Final impact type: `execution-context-integrity`
Final confidence: `medium`
Final tags: `vm, evm, native-contract-hook, callcode, delegatecall, execution-context, security-hardening`

The supplied evidence does not prove a concrete exploitable vulnerability, but it does support retaining the case as security hardening. The patch moves native contract hook dispatch into the interpreter and adds an explicit CodeAddr == Address gate with a comment to ignore CALLCODE or DELEGATECALL, which tightens a security-sensitive VM execution boundary. The feature additions and error-handling changes should not be treated as a proven security fix by themselves.

## Security Evidence

1. Commit subject explicitly says it improves security of the VM contract hook.
2. Interpreter.Run now invokes the contract hook only when contract.CodeAddr is non-nil and equals contract.Address().
3. The added code explicitly comments that CALLCODE or DELEGATECALL should be ignored for hook dispatch.
4. Runtime and builtin bridge now pass authoritative EVM and Contract objects instead of separately threaded call parameters.

## Missing Evidence

1. No exploit path or vulnerable pre-patch scenario is shown.
2. No test demonstrates that CALLCODE or DELEGATECALL could misuse the native hook before the patch.
3. No concrete impact such as authorization bypass, state corruption, consensus failure, or node crash is proven.
4. The prototype_energy and prototype_transferEnergy additions are not shown to be vulnerability fixes.

## Claim Boundaries

1. Classify as security-hardening, not security-fix.
2. Do not claim a confirmed liveness failure from the supplied evidence.
3. Do not claim remote exploitability or consensus impact.
4. The supported claim is limited to tightening native contract hook dispatch across direct execution versus CALLCODE/DELEGATECALL contexts.
